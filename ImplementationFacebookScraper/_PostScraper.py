import logging
import requests
from datetime import datetime, timedelta
from dateutil.parser import parse
from unidecode import unidecode
import re


class _PostScraper():        
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

    def _post_formalizer(post_object, GMT):
        """
        Formalizing result object post that obtained from Facebook GraphAPI

        Parameters
        ----------
        post_object : dict
                      A dictionary that contains fields from Facebook GraphAPI

        GMT : string
              Define GMT that wants to be used with format +{hours}:{minutes}. 
              Example: `+7:00`, `-12:30`

        Returns
        -------
        New post object with formal format as type dict.

        """
        if 'from' in post_object:
            name = unidecode(post_object['from']['name']).replace('\n',' ').replace('\t',' ').replace('\r',' ')
            name = re.sub('^\s+','', name)
            name = re.sub('\s+$','', name)
            if len(re.findall('\S', name)) < 1:
                name = 'N/A'
            from_id = post_object['from']['id']
            post_object.pop('from')
        else:
            name = 'N/A'
            from_id = 'N/A'
        post_object.update({'created_time': _PostScraper._time_converter(post_object['created_time'], GMT),
                            'from_name': name,
                            'from_id': from_id,
                            'comments': post_object['comments']['count'],
                            'GMT': GMT})
        if 'likes' in post_object:
            post_object.update({'likes': post_object['likes']['count']})
        else:
            post_object.update({'likes': 0})

        if 'shares' in post_object:
            post_object.update({'shares': post_object['shares']['count']})
        else:
            post_object.update({'shares': 0})

        if 'message' in post_object:
            message = unidecode(post_object['message']).replace('\n',' ').replace('\t',' ').replace('\r',' ')
            message = re.sub('^\s+','', message)
            message = re.sub('\s+$','', message)
            if len(re.findall('\S', message)) < 1:
                message = 'N/A'
            post_object.update({'message': message})
        else:
            post_object.update({'message': 'N/A'})

        if 'story' in post_object:
            story = unidecode(post_object['story']).replace('\n',' ').replace('\t',' ').replace('\r',' ')
            story = re.sub('^\s+','', story)
            story = re.sub('\s+$','', story)
            if len(re.findall('\S', story)) < 1:
                story = 'N/A'
            post_object.update({'story': story})
        else:
            post_object.update({'story': 'N/A'})

        if 'reactions' in post_object:
            reactions = []
            for reaction in post_object['reactions']['data']:
                name = unidecode(reaction['name']).replace('\n',' ').replace('\t',' ').replace('\r',' ')
                name = re.sub('^\s+','', name)
                name = re.sub('\s+$','', name)
                if len(re.findall('\S', name)) < 1:
                    name = 'N/A'
                reaction.update({'name': name})
                reactions.append(reaction)
            post_object.update({'reactions': reactions})
        else:
            post_object.update({'reactions': []})
        return post_object

    def _post_storer(storer, objects, min_date_limit, GMT, max_post_limit=None):
        """
        A function to append the scraped posts on list `storer` if conditions are correct

        Parameters
        ----------
        storer : list
                 Reserved list to store scraped posts.

        objects : dict
                  Scraped posts obtained from Facebook GraphAPI.

        min_date_limit : datetime.date
                         Defined date. An object will be stored if conditions are correct.

        GMT : string
              Define GMT that wants to be used with format +{hours}:{minutes}. 
              Example: `+7:00`, `-12:30`

        Returns
        -------
        bool
        """
        if (max_post_limit is None):
            for obj in objects['data']:
                obj = _PostScraper._post_formalizer(obj, GMT)
                if obj['created_time'].date() > min_date_limit:
                    storer.append(obj)
                    condition = True
                else:
                    condition = False
            if len(objects['data']) == 0:
                condition = False
        else:
            for obj in objects['data']:
                obj = _PostScraper._post_formalizer(obj, GMT)
                if len(storer) < max_post_limit:
                    storer.append(obj)
                    condition = True
                else:
                    condition = False
                    break
            if len(objects['data']) == 0:
                condition = False
        return condition

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

    def get_post_data(engine, target_id, add_field=None, remove_field=None, day_limit=7, count_limit=None, GMT='+7:00'):
        """
        Scraping user posts using Facebook GraphAPI based on user ID. Facebook access token is needed.

        Parameters
        ----------
        engine : facebook.GraphAPI
                 Authenticated API using existing facebook access token.

        target_id : string
                  A facebook user id. See this if you dont know https://findmyfbid.in/

        add_field : list, optional
                    See this documentation https://developers.facebook.com/docs/graph-api/reference/post
                    to know available field options.

        remove_field : list, optional
                       Default fields are `from, story, id, created_time, message, likes, comments, 
                       shares, reactions, status_type, type`. If you want to remove some fields, 
                       just input that fields as list and put to this parameter.

        day_limit : integer, optional
                    Determine how many days ago the data you want to retrieve.
                    Used only if parameter `count_limit` is None. Ignored if count_limit specified.

        count_limit : integer, optional
                      Determine how many the posts data you want to retrieve. 

        GMT : string
              Define GMT that wants to be used with format +{hours}:{minutes}. 
              Example: `+7:00`, `-12:30`

        """
        posts = []

        # calculate day limit
        if (count_limit is None):
            max_date_limit = datetime.now().date()
            min_date_limit = max_date_limit - timedelta(days=day_limit)
            max_post_limit = None
        else:
            max_post_limit = count_limit
            min_date_limit = None

        # set up the fields
        fields = 'from, story, id, created_time, message, likes, comments, shares, reactions, status_type, type,'
        if (add_field is not None):
            field_adder = ', '.join(add_field)
            fields = '%s, %s' % (fields, field_adder)
        if (remove_field is not None):
            for i in remove_field:
                fields = fields.replace('%s,' % i, '')
        fields = fields.replace(' ','')
        fields = re.sub('\,$','',fields)

        # checking facebook id is exists
        status = _PostScraper._target_validation(engine, target_id)
        if (status is not None):

            # requesting posts data from Facebook GraphAPI
            if 'privacy' not in status:
                reload_count = 0
                while True:
                    try:
                        objects = engine.get_connections(id=target_id, connection_name='posts', fields=fields)
                        break
                    except Exception as e:
                        reload_count += 1
                        logging.error('We will trying again! %i %s' % (reload_count, str(e)))
                        if not str(e).startswith('HTTPSConnectionPool'):
                            if reload_count == 10:
                                logging.error('Skipping the process because : %s' % str(e))
                                objects = {'data':[]}
                                break
                        else:
                            if reload_count == 50:
                                logging.error('Skipping the process because : %s' % str(e))
                                objects = {'data':[]}
                                break
            else:
                reload_count = 0
                while True:
                    try:
                        objects = engine.get_connections(id=target_id, connection_name='feed', fields=fields)
                        break
                    except Exception as e:
                        reload_count += 1
                        logging.error(str(e))
                        if reload_count == 10:
                            logging.error('Skipping the process because : %s' % str(e))
                            objects = {'data':[]}
                            break

            # storing the posts data and navigating to the next page to get more data if conditions are correct
            if (_PostScraper._post_storer(storer=posts, objects=objects, min_date_limit=min_date_limit, GMT=GMT, max_post_limit=max_post_limit) is True):
                if len(posts) > 0:
                    while True:
                        logging.info('Scraping %s (%s) posts %i !' % (status['name'], status['id'], len(posts)))
                        if 'next' in objects['paging']:
                            next_page = objects['paging']['next']
                        else:
                            logging.info('Scraping %s (%s) posts complete! Total : %i' % (status['name'], status['id'], len(posts)))
                            break
                        reload_count = 0
                        while True:
                            try:
                                objects = requests.get(next_page).json()
                                break
                            except Exception as e:
                                reload_count += 1
                                logging.error('We will trying again! %i %s' % (reload_count, str(e)))
                                if not str(e).startswith('HTTPSConnectionPool'):
                                    if reload_count == 10:
                                        logging.error('Skipping the process because : %s' % str(e))
                                        objects = {'data':[], 'paging':{'empty':str(e)}}
                                        break
                                else:
                                    if reload_count == 50:
                                        logging.error('Skipping the process because : %s' % str(e))
                                        objects = {'data':[], 'paging':{'empty':str(e)}}
                                        break

                        if (_PostScraper._post_storer(storer=posts, objects=objects, min_date_limit=min_date_limit, GMT=GMT, max_post_limit=max_post_limit) is False):
                            logging.info('Scraping %s (%s) posts complete! Total : %i' % (status['name'], status['id'], len(posts)))
                            break
                else:
                    logging.info('Scraping %s (%s) posts complete! Total : %i' % (status['name'], status['id'], len(posts)))
            else:
                logging.info('Scraping %s (%s) posts complete! Total : %i' % (status['name'], status['id'], len(posts)))
        return posts
