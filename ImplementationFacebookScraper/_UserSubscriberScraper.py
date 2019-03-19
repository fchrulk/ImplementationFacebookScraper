import logging
import re
from unidecode import unidecode
import requests

class _UserSubscriberScraper():
    def _target_validation(engine, target_id):
        """
        Validating the target is exists or not

        Parameters
        ----------
        engine : facebook.GraphAPI
                 Authenticated API using existing facebook access token.

        target_id : string
                  A facebook user id. See this if you dont know https://findmyfbid.in/
        """
        try:
            return engine.get_object(target_id)
        except:
            logging.error('Target %s not found!' % target_id)
            return None

    def _basic_info_formalizer(target, basic_info_object):
        """
        Formalizing result object post that obtained from Facebook GraphAPI

        Parameters
        ----------
        target : dict
                 A dictionary that contains minimum information of target
                 
        basic_info_object : dict
                            A dictionary that contains fields from Facebook GraphAPI

        Returns
        -------
        New basic info object with formal format as type dict.

        """
        def if_exists(basic_info_object, field_names):
            for field_name in field_names:
                if field_name in basic_info_object:
                    replacing = unidecode(basic_info_object[field_name]).replace('\n',' ').replace('\t',' ').replace('\r',' ')
                    replacing = re.sub('^\s+','', replacing)
                    replacing = re.sub('\s+$','', replacing)
                    if len(re.findall('\S', replacing)) < 1:
                        replacing = 'N/A'
                    basic_info_object.update({field_name: replacing})
                else:
                    basic_info_object.update({field_name: 'N/A'})
        
        if_exists(basic_info_object=basic_info_object, field_names=['name','religion','political',
            'gender','relationship_status','email','mobile_phone', 'birthday'])
        
        if 'hometown' in basic_info_object:
            basic_info_object.update({'hometown': basic_info_object['hometown']['name']})
        else:
            basic_info_object.update({'hometown': 'N/A'})

        if 'location' in basic_info_object:
            basic_info_object.update({'location': basic_info_object['location']['name']})
        else:
            basic_info_object.update({'location': 'N/A'})

        if 'address' in basic_info_object:
            if ('city' not in basic_info_object['address']):
                basic_info_object['address'].update({'city': 'N/A'})
            if ('country' not in basic_info_object['address']):
                basic_info_object['address'].update({'country': 'N/A'})
            if ('state' not in basic_info_object['address']):
                basic_info_object['address'].update({'state': 'N/A'})
            if ('street' not in basic_info_object['address']):
                basic_info_object['address'].update({'street': 'N/A'})
            if ('zip' not in basic_info_object['address']):
                basic_info_object['address'].update({'zip': 'N/A'})
            if ('latitude' not in basic_info_object['address']):
                basic_info_object['address'].update({'latitude': 'N/A'})
            if ('longitude' not in basic_info_object['address']):
                basic_info_object['address'].update({'longitude': 'N/A'})
        else:
            basic_info_object.update({'address': {'city':'N/A', 
                                                  'country':'N/A', 
                                                  'state':'N/A', 
                                                  'street':'N/A',
                                                  'zip':'N/A',
                                                  'latitude':'N/A',
                                                  'longitude':'N/A'}})
        
        if 'education' in basic_info_object:
            for i in range(len(basic_info_object['education'])):
                origin = basic_info_object['education'][i]
                basic_info_object['education'][i].update({'school_name': origin['school']['name']})
                basic_info_object['education'][i].update({'education_type': origin['type']})
                basic_info_object['education'][i].pop('school')
                basic_info_object['education'][i].pop('type')
                # basic_info_object['education'][i].pop('id')
                if 'year' in basic_info_object['education'][i]:
                    basic_info_object['education'][i].pop('year')
                if 'degree' in basic_info_object['education'][i]:
                    degree = basic_info_object['education'][i]['degree']['name']
                    basic_info_object['education'][i].update({'degree': degree})
                else:
                    basic_info_object['education'][i].update({'degree': 'N/A'})
                if 'concentration' in basic_info_object['education'][i]:
                    concentrations = []
                    for concentration in basic_info_object['education'][i]['concentration']:
                        concentrations.append(concentration['name'])
                    basic_info_object['education'][i].update({'concentration': concentrations})
                else:
                    basic_info_object['education'][i].update({'concentration': []})
        else:
            basic_info_object.update({'education': []})

        if 'work' in basic_info_object:
            for i in range(len(basic_info_object['work'])):
                origin = basic_info_object['work'][i]
                basic_info_object['work'][i].update({'company': origin['employer']['name']})
                basic_info_object['work'][i].pop('employer')
                # basic_info_object['work'][i].pop('id')
                if 'position' in basic_info_object['work'][i]:
                    position = basic_info_object['work'][i]['position']['name']
                    basic_info_object['work'][i].update({'position': position})
                else:
                    basic_info_object['work'][i].update({'position': 'N/A'})
                if 'location' in basic_info_object['work'][i]:
                    location = basic_info_object['work'][i]['location']['name']
                    basic_info_object['work'][i].update({'location': location})
                else:
                    basic_info_object['work'][i].update({'location': 'N/A'})
                if 'start_date' not in basic_info_object['work'][i]:
                    basic_info_object['work'][i].update({'start_date': 'N/A'})
                if 'end_date' not in basic_info_object['work'][i]:
                    basic_info_object['work'][i].update({'end_date': 'N/A'})
        else:
            basic_info_object.update({'work': []})

        if 'subscribers' in basic_info_object:
            basic_info_object.update({'subscriber_count': basic_info_object['subscribers']['summary']['total_count']})
            basic_info_object.pop('subscribers')
        else:
            basic_info_object.update({'friend_count': 0})

        basic_info_object.update({'from_name': target['name']})
        basic_info_object.update({'from_id': target['id']})
        return basic_info_object

    def _subscriber_storer(engine, target, storer, objects, max_subscriber_limit=None, friend_count=False):
        """
        A function to append the scraped joined interests on list `storer` if conditions are correct

        Parameters
        ----------
        storer : list
                 Reserved list to store scraped joined interests.

        objects : dict
                  Scraped joined interests obtained from Facebook GraphAPI.

        max_subscriber_limit : integer, optional
                               Determine how many the subscribers data you want to retrieve. 

        GMT : string
              Define GMT that wants to be used with format +{hours}:{minutes}. 
              Example: `+7:00`, `-12:30`

        friend_count : boolean, optional
                       Default is False. Whether to get count of friends on each subscriber or not.
                       (will takes more time, better not get it)

        Returns
        -------
        bool
        """
        if (max_subscriber_limit is not None):
            for obj in objects['data']:
                obj = _UserSubscriberScraper._basic_info_formalizer(target, obj)
                if len(storer) < max_subscriber_limit:
                    if (friend_count is True):
                        friends = engine.get_object(obj['id'], fields='friends.limit(0)')
                        if 'friends' in friends:
                            obj.update({'friend_count': friends['friends']['summary']['total_count']})
                        else:
                            obj.update({'friend_count': 0})
                    storer.append(obj)
                    condition = True
                else:
                    condition = False
                    break
        else:
            for obj in objects['data']:
                obj = _UserSubscriberScraper._basic_info_formalizer(target, obj)
                if (friend_count is True):
                    friends = engine.get_object(obj['id'], fields='friends.limit(0)')
                    if 'friends' in friends:
                            obj.update({'friend_count': friends['friends']['summary']['total_count']})
                    else:
                        obj.update({'friend_count': 0})
                storer.append(obj)
                condition = True
        if len(objects['data']) == 0:
            condition = False
        return condition

    def get_subscriber_data(engine, target_id, add_field=None, remove_field=None, count_limit=None, friend_count=False):
        """
        Scraping subscribers of target using Facebook GraphAPI based on user ID. Facebook access token is needed.

        Parameters
        ----------
        engine : facebook.GraphAPI
                 Authenticated API using existing facebook access token.

        target_id : string
                  A facebook user id. See this if you dont know https://findmyfbid.in/

        add_field : list, optional
                    See this documentation https://developers.facebook.com/docs/graph-api/reference/user
                    to know available field options.

        remove_field : list, optional
                       Default fields are `name, id, gender, birthday, relationship_status, religion,
                       political, mobile_phone, email, address, hometown, location, education, work`. 
                       If you want to remove some fields, just input that fields as list and put to this parameter.

        count_limit : integer, optional
                      Determine how many the subscribers data you want to retrieve.

        friend_count : boolean, optional
                       Default is False. Whether to get count of friends on each subscriber or not.
                       (will takes more time, better not get it)
        """
        subscribers = []

        max_subscriber_limit = count_limit

        # set up the fields
        fields = 'name, id, gender, birthday, relationship_status, religion, political, '\
                 'mobile_phone, email, address, hometown, location, education, work, subscribers.limit(0),'
        if (add_field is not None):
            field_adder = ', '.join(add_field)
            fields = '%s, %s' % (fields, field_adder)
        if (remove_field is not None):
            for i in remove_field:
                fields = fields.replace('%s,' % i, '')
        fields = fields.replace(' ','')
        fields = re.sub('\,$','',fields)

        # checking facebook id is exists
        status = _UserSubscriberScraper._target_validation(engine, target_id)
        if (status is not None):
            
            # requesting subscribers data from Facebook GraphAPI
            url_request_subscribers = 'https://graph.facebook.com/v1.0/%s/subscribers?access_token=%s&fields=%s'\
                                       % (target_id, engine.access_token, fields)
            objects = requests.get(url_request_subscribers).json()

            # storing the subscribers data and navigating to the next page to get more data if conditions are correct
            if (_UserSubscriberScraper._subscriber_storer(engine=engine, target=status, storer=subscribers, objects=objects, max_subscriber_limit=max_subscriber_limit, friend_count=friend_count) is True):
                if len(subscribers) > 0:
                    while True:
                        logging.info('Scraping %s (%s) subscribers %i !' % (status['name'], status['id'], len(subscribers)))
                        if 'next' in objects['paging']:
                            next_page = objects['paging']['next']
                        else:
                            logging.info('Scraping %s (%s) subscribers complete! Total : %i' % (status['name'], status['id'], len(subscribers)))
                            break
                        objects = requests.get(next_page).json()
                        if (_UserSubscriberScraper._subscriber_storer(engine=engine, target=status, storer=subscribers, objects=objects, max_subscriber_limit=max_subscriber_limit, friend_count=friend_count) is False):
                            logging.info('Scraping %s (%s) subscribers complete! Total : %i' % (status['name'], status['id'], len(subscribers)))
                            break
                else:
                    logging.info('Scraping %s (%s) subscribers complete! Total : %i' % (status['name'], status['id'], len(subscribers)))
            else:
                logging.info('Scraping %s (%s) subscribers complete! Total : %i' % (status['name'], status['id'], len(subscribers)))
        return subscribers