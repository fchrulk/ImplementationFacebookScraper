import logging
import re
from unidecode import unidecode
import requests

class _PageBasicInfoScraper():
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

    def _interest_formalizer(interest_object):
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
        return interest_object

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
        fields = 'name, id, about, general_info, verification_status, website, emails, '\
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
        status = _PageBasicInfoScraper._target_validation(engine, target_id)
        if (status is not None):
            
            # requesting basic information from Facebook GraphAPI
            basic_info = engine.get_object(id=target_id, fields=fields)
            basic_info = _PageBasicInfoScraper._interest_formalizer(interest_object=basic_info)
            logging.info('Scraping %s (%s) basic information complete!' % (status['name'], status['id']))
            return basic_info