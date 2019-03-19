import logging
import re
from unidecode import unidecode
import requests
from datetime import datetime, timedelta
from dateutil.parser import parse

class _UserGroupScraper():
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
            logging.error('Target %s not found! Getting joined groups by target failed!' % target_id)
            return None

    def _group_formalizer(target, group_object, GMT):
        """
        Formalizing result object group that obtained from Facebook GraphAPI

        Parameters
        ----------
        target : dict
                 A dictionary that contains minimum information of target

        group_object : dict
                       A dictionary that contains fields from Facebook GraphAPI

        GMT : string
              Define GMT that wants to be used with format +{hours}:{minutes}. 
              Example: `+7:00`, `-12:30`

        Returns
        -------
        New group object with formal format as type dict.

        """
        def if_exists(group_object, field_names):
            for field_name in field_names:
                if field_name in group_object:
                    replacing = unidecode(group_object[field_name]).replace('\n',' ').replace('\t',' ').replace('\r',' ')
                    replacing = re.sub('^\s+','', replacing)
                    replacing = re.sub('\s+$','', replacing)
                    if len(re.findall('\S', replacing)) < 1:
                        replacing = 'N/A'
                    group_object.update({field_name: replacing})
                else:
                    group_object.update({field_name: 'N/A'})

        fields = 'name, id, privacy, description, email, member_count, updated_time, administrator,'
        if_exists(group_object, field_names=['name', 'description', 'email'])
        group_object.update({'group_name': group_object['name']})
        group_object.pop('name')
        group_object.update({'group_description': group_object['description']})
        group_object.pop('description')
        group_object.update({'group_email': group_object['email']})
        group_object.pop('email')
        group_object.update({'group_id': group_object['id']})
        group_object.pop('id')
        group_object.update({'group_privacy': group_object['privacy'].title()})
        group_object.pop('privacy')
        group_object.update({'group_member_count': group_object['member_count']})
        group_object.pop('member_count')
        group_object.update({'group_recently_active': _UserGroupScraper._time_converter(group_object['updated_time'], GMT)})
        group_object.pop('updated_time')
        group_object.update({'is_target_administrator': group_object['administrator']})
        group_object.pop('administrator')
        group_object.update({'from_name': target['name']})
        group_object.update({'from_id': target['id']})
        return group_object


    def _group_storer(target, storer, objects, GMT, max_group_limit=25):
        """
        A function to append the scraped joined groups on list `storer` if conditions are correct

        Parameters
        ----------
        storer : list
                 Reserved list to store scraped joined groups.

        objects : dict
                  Scraped joined groups obtained from Facebook GraphAPI.

        max_group_limit : integer, optional
                          Determine how many the groups data you want to retrieve. 

        GMT : string
              Define GMT that wants to be used with format +{hours}:{minutes}. 
              Example: `+7:00`, `-12:30`

        Returns
        -------
        bool
        """
        for obj in objects['data']:
            obj = _UserGroupScraper._group_formalizer(target, obj, GMT)
            if len(storer) < max_group_limit:
                storer.append(obj)
                condition = True
            else:
                condition = False
                break
        if len(objects['data']) == 0:
            condition = False
        return condition

    def get_user_joined_group(engine, target_id, add_field=None, remove_field=None, count_limit=25, GMT='+7:00'):
        """
        Scraping joined groups by target using Facebook GraphAPI based on user ID. Facebook access token is needed.

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
                      Determine how many the groups data you want to retrieve. 

        GMT : string
              Define GMT that wants to be used with format +{hours}:{minutes}. 
              Example: `+7:00`, `-12:30`
        """
        groups = []

        max_group_limit = count_limit

        # set up the fields
        fields = 'name, id, privacy, description, email, member_count, updated_time, administrator,'
        if (add_field is not None):
            field_adder = ', '.join(add_field)
            fields = '%s, %s' % (fields, field_adder)
        if (remove_field is not None):
            for i in remove_field:
                fields = fields.replace('%s,' % i, '')
        fields = fields.replace(' ','')
        fields = re.sub('\,$','',fields)

        # checking facebook id is exists
        status = _UserGroupScraper._target_validation(engine, target_id)
        if (status is not None):

            # requesting joined groups by target from Facebook GraphAPI
            objects = engine.get_connections(target_id, 'groups', fields=fields)

            # storing the joined groups data and navigating to the next page to get more data if conditions are correct
            if (_UserGroupScraper._group_storer(target=status, storer=groups, objects=objects, GMT=GMT, max_group_limit=max_group_limit) is True):
                if len(groups) > 0:
                    while True:
                        logging.info('Scraping %s (%s) joined groups %i !' % (status['name'], status['id'], len(groups)))
                        if 'next' in objects['paging']:
                            next_page = objects['paging']['next']
                        else:
                            logging.info('Scraping %s (%s) joined groups complete! Total : %i' % (status['name'], status['id'], len(groups)))
                            break
                        objects = requests.get(next_page).json()
                        if (_UserGroupScraper._group_storer(target=status, storer=groups, objects=objects, GMT=GMT, max_group_limit=max_group_limit) is False):
                            logging.info('Scraping %s (%s) joined groups complete! Total : %i' % (status['name'], status['id'], len(groups)))
                            break
                else:
                    logging.info('Scraping %s (%s) joined groups complete! Total : %i' % (status['name'], status['id'], len(groups)))
            else:
                logging.info('Scraping %s (%s) joined groups complete! Total : %i' % (status['name'], status['id'], len(groups)))
        return groups

