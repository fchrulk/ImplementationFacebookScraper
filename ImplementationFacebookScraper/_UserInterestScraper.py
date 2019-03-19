import logging
import re
from unidecode import unidecode
import requests
from datetime import datetime, timedelta
from dateutil.parser import parse

class _UserInterestScraper():
    def _time_converter(timestring, GMT):
        """
        Converting timestring to datetime.datetime and also change the time based on GMT.

        Parameters
        ----------
        timestring : string
                     Time with string dtype

        GMT : string
              Define GMT that wants to be used with format +{hours}:{minutes}. 
              Example: `+7:00`, `-12:30`

        Returns
        -------
        datetime.datetime

        """
        timestring = parse(timestring, ignoretz=True)
        if '+' in GMT:
            GMT = GMT.split(':')
            h, m = (int(GMT[0].replace('+','')), int(GMT[1]))
            return timestring + timedelta(hours=h, minutes=m)
        else:
            GMT = GMT.split(':')
            h, m = (int(GMT[0].replace('-','')), int(GMT[1]))
            return timestring - timedelta(hours=h, minutes=m)

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
            logging.error('Target %s not found! Getting target interests failed!' % target_id)
            return None

    def _interest_formalizer(target, interest_object, GMT):
        """
        Formalizing result object interest that obtained from Facebook GraphAPI

        Parameters
        ----------
        target : dict
                 A dictionary that contains minimum information of target

        interest_object : dict
                          A dictionary that contains fields from Facebook GraphAPI

        GMT : string
              Define GMT that wants to be used with format +{hours}:{minutes}. 
              Example: `+7:00`, `-12:30`

        Returns
        -------
        New interest object with formal format as type dict.

        """
        def if_exists(interest_object, field_names):
            for field_name in field_names:
                if field_name in interest_object:
                    replacing = unidecode(interest_object[field_name]).replace('\n',' ').replace('\t',' ').replace('\r',' ')
                    replacing = re.sub('^\s+','', replacing)
                    replacing = re.sub('\s+$','', replacing)
                    if len(re.findall('\S', replacing)) < 1:
                        replacing = 'N/A'
                    interest_object.update({field_name: replacing})
                else:
                    interest_object.update({field_name: 'N/A'})

        if_exists(interest_object, field_names=['name', 'about', 'general_info', 'website'])
        interest_object.update({'interest_name': interest_object['name']})
        interest_object.pop('name')
        interest_object.update({'interest_about': interest_object['about']})
        interest_object.pop('about')
        interest_object.update({'interest_general_information': interest_object['general_info']})
        interest_object.pop('general_info')
        interest_object.update({'interest_id': interest_object['id']})
        interest_object.pop('id')
        interest_object.update({'interest_fan_count': interest_object['fan_count']})
        interest_object.pop('fan_count')
        interest_object.update({'interest_were_here_count': interest_object['were_here_count']})
        interest_object.pop('were_here_count')
        interest_object.update({'interest_verification_status': interest_object['verification_status'].replace('_',' ').title()})
        interest_object.pop('verification_status')
        interest_object.update({'interest_website': interest_object['website']})
        interest_object.pop('website')

        if 'rating_count' in interest_object:
            interest_object.update({'interest_rating_count': interest_object['rating_count']})
            interest_object.pop('rating_count')
        else:
            interest_object.update({'interest_overall_star_rating': 0})

        if 'overall_star_rating' in interest_object:
            interest_object.update({'interest_overall_star_rating': interest_object['overall_star_rating']})
            interest_object.pop('overall_star_rating')
        else:
            interest_object.update({'interest_overall_star_rating': 0.0})

        if 'talking_about_count' in interest_object:
            interest_object.update({'interest_talking_about_count': interest_object['talking_about_count']})
            interest_object.pop('talking_about_count')
        else:
            interest_object.update({'interest_talking_about_count': 0})

        interest_object.update({'interests_created_time': _UserInterestScraper._time_converter(interest_object['created_time'], GMT)})
        interest_object.pop('created_time')

        categories = []
        if 'category_list' in interest_object:
            for cat in interest_object['category_list']:
                categories.append(cat['name'])
            interest_object.update({'interest_categories': categories})
            interest_object.pop('category_list')
        else:
            interest_object.update({'interest_categories': []})

        emails = []
        if 'emails' in interest_object:
            for email in interest_object['emails']:
                email = unidecode(email).replace('\n',' ').replace('\t',' ').replace('\r',' ')
                email = re.sub('^\s+','', email)
                email = re.sub('\s+$','', email)
                if len(re.findall('\S', email)) < 1:
                    email = None
                if (email is not None):
                    emails.append(email)
            interest_object.update({'interest_emails': emails})
            interest_object.pop('emails')
        else:
            interest_object.update({'interest_emails': []})
        
        interest_object.update({'from_name': target['name']})
        interest_object.update({'from_id': target['id']})
        return interest_object


    def _interest_storer(target, storer, objects, GMT, max_interest_limit=25):
        """
        A function to append the scraped interests on list `storer` if conditions are correct

        Parameters
        ----------
        storer : list
                 Reserved list to store scraped interests.

        objects : dict
                  Scraped interests obtained from Facebook GraphAPI.

        max_interest_limit : integer, optional
                             Determine how many the interests data you want to retrieve. 

        GMT : string
              Define GMT that wants to be used with format +{hours}:{minutes}. 
              Example: `+7:00`, `-12:30`

        Returns
        -------
        bool
        """
        for obj in objects['data']:
            obj = _UserInterestScraper._interest_formalizer(target, obj, GMT)
            if len(storer) < max_interest_limit:
                storer.append(obj)
                condition = True
            else:
                condition = False
                break
        if len(objects['data']) == 0:
            condition = False
        return condition

    def get_user_interest(engine, target_id, add_field=None, remove_field=None, count_limit=25, GMT='+7:00'):
        """
        Scraping target interests using Facebook GraphAPI based on user ID. Facebook access token is needed.

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
                       Default fields are `name, id, privacy, description, email, member_count, updated_time, administrator`. 
                       If you want to remove some fields, just input that fields as list and put to this parameter.

        count_limit : integer, optional
                      Determine how many the interests data you want to retrieve. 

        GMT : string
              Define GMT that wants to be used with format +{hours}:{minutes}. 
              Example: `+7:00`, `-12:30`
        """
        interests = []

        max_interest_limit = count_limit

        # set up the fields
        fields = 'name, id, about, general_info, verification_status, created_time, website, emails, '\
                 'category_list, fan_count, talking_about_count, overall_star_rating, rating_count, were_here_count,'
        if (add_field is not None):
            field_adder = ', '.join(add_field)
            fields = '%s, %s' % (fields, field_adder)
        if (remove_field is not None):
            for i in remove_field:
                fields = fields.replace('%s,' % i, '')
        fields = fields.replace(' ','')
        fields = re.sub('\,$','',fields)

        # checking facebook id is exists
        status = _UserInterestScraper._target_validation(engine, target_id)
        if (status is not None):

            # requesting interests by target from Facebook GraphAPI
            objects = engine.get_connections(target_id, 'likes', fields=fields)

            # storing the interests data and navigating to the next page to get more data if conditions are correct
            if (_UserInterestScraper._interest_storer(target=status, storer=interests, objects=objects, GMT=GMT, max_interest_limit=max_interest_limit) is True):
                if len(interests) > 0:
                    while True:
                        logging.info('Scraping %s (%s) interests %i !' % (status['name'], status['id'], len(interests)))
                        if 'next' in objects['paging']:
                            next_page = objects['paging']['next']
                        else:
                            logging.info('Scraping %s (%s) interests complete! Total : %i' % (status['name'], status['id'], len(interests)))
                            break
                        objects = requests.get(next_page).json()
                        if (_UserInterestScraper._interest_storer(target=status, storer=interests, objects=objects, GMT=GMT, max_interest_limit=max_interest_limit) is False):
                            logging.info('Scraping %s (%s) interests complete! Total : %i' % (status['name'], status['id'], len(interests)))
                            break
                else:
                    logging.info('Scraping %s (%s) interests complete! Total : %i' % (status['name'], status['id'], len(interests)))
            else:
                logging.info('Scraping %s (%s) interests complete! Total : %i' % (status['name'], status['id'], len(interests)))
        return interests

