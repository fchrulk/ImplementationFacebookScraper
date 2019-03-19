import logging
import re
from unidecode import unidecode
import requests

class _UserBasicInfoScraper():
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

    def _basic_info_formalizer(basic_info_object):
        """
        Formalizing result object post that obtained from Facebook GraphAPI

        Parameters
        ----------
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
                basic_info_object['education'][i].pop('id')
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
                basic_info_object['work'][i].pop('id')
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

        if 'friends' in basic_info_object:
            basic_info_object.update({'friend_count': basic_info_object['friends']['summary']['total_count']})
            basic_info_object.pop('friends')
        else:
            basic_info_object.update({'friend_count': 0})


        return basic_info_object

    def get_basic_info(engine, target_id, add_field=None, remove_field=None):
        """
        Scraping target basic information using Facebook GraphAPI based on user ID. Facebook access token is needed.

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
        """

        # set up the fields
        fields = 'name, id, gender, birthday, relationship_status, religion, political, '\
                 'mobile_phone, email, address, hometown, location, education, work, friends.limit(0),'
        if (add_field is not None):
            field_adder = ', '.join(add_field)
            fields = '%s, %s' % (fields, field_adder)
        if (remove_field is not None):
            for i in remove_field:
                fields = fields.replace('%s,' % i, '')
        fields = fields.replace(' ','')
        fields = re.sub('\,$','',fields)

        # checking facebook id is exists
        status = _UserBasicInfoScraper._target_validation(engine, target_id)
        if (status is not None):
            
            # requesting basic information from Facebook GraphAPI
            basic_info = engine.get_object(id=target_id, fields=fields)
            url_request_subscribers = 'https://graph.facebook.com/v1.0/%s/subscribers?access_token=%s&limit=0' \
                                       % (target_id, engine.access_token)
            subscribers = requests.get(url_request_subscribers).json()['summary']['total_count']
            basic_info.update({'subscriber_count': subscribers})
            basic_info = _UserBasicInfoScraper._basic_info_formalizer(basic_info_object=basic_info)
            logging.info('Scraping %s (%s) basic information complete!' % (status['name'], status['id']))
            return basic_info