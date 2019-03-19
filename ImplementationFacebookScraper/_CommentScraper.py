import logging
import requests
from datetime import datetime, timedelta
from dateutil.parser import parse
from unidecode import unidecode
import re


class _CommentScraper():        
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

    def _comment_formalizer(comment_object, GMT):
        """
        Formalizing result object post that obtained from Facebook GraphAPI

        Parameters
        ----------
        comment_object : dict
                         A dictionary that contains fields from Facebook GraphAPI

        GMT : string
              Define GMT that wants to be used with format +{hours}:{minutes}. 
              Example: `+7:00`, `-12:30`

        Returns
        -------
        New comment object with formal format as type dict.

        """
        if 'from' in comment_object:
            name = unidecode(comment_object['from']['name']).replace('\n',' ').replace('\t',' ').replace('\r',' ')
            name = re.sub('^\s+','', name)
            name = re.sub('\s+$','', name)
            if len(re.findall('\S', name)) < 1:
                name = 'N/A'
            from_id = comment_object['from']['id']
            comment_object.pop('from')
        else:
            name = 'N/A'
            from_id = 'N/A'
        comment_object.update({'created_time': _CommentScraper._time_converter(comment_object['created_time'], GMT),
                               'from_name': name,
                               'from_id': from_id,
                               'comments': comment_object['comment_count'],
                               'likes': comment_object['like_count'],
                               'GMT': GMT})
        comment_object.pop('comment_count')
        comment_object.pop('like_count')
        if 'message' in comment_object:
            message = unidecode(comment_object['message']).replace('\n',' ').replace('\t',' ').replace('\r',' ')
            message = re.sub('^\s+','', message)
            message = re.sub('\s+$','', message)
            if len(re.findall('\S', message)) < 1:
                message = 'N/A'
            comment_object.update({'message': message})
        else:
            comment_object.update({'message': 'N/A'})

        if 'reactions' in comment_object:
            reactions = []
            for reaction in comment_object['reactions']['data']:
                name = unidecode(reaction['name']).replace('\n',' ').replace('\t',' ').replace('\r',' ')
                name = re.sub('^\s+','', name)
                name = re.sub('\s+$','', name)
                if len(re.findall('\S', name)) < 1:
                    name = 'N/A'
                reaction.update({'name': name})
                reactions.append(reaction)
            comment_object.update({'reactions': reactions})
        else:
            comment_object.update({'reactions': []})

        if 'attachment' in comment_object:
            comment_object.update({'comment_type': comment_object['attachment']['type'],
                                   'media_facebook_url': comment_object['attachment']['url']})
            if 'media' in comment_object['attachment']:
                comment_object.update({'media_image_url': comment_object['attachment']['media']['image']['src']})
            else:
                comment_object.update({'media_image_url': 'N/A'})
            comment_object.pop('attachment')
        else:
            comment_object.update({'comment_type': 'text',
                                   'media_facebook_url': 'N/A',
                                   'media_image_url': 'N/A'})
        return comment_object

    def _comment_storer(storer, objects, GMT, max_comment_limit='all'):
        """
        A function to append the scraped comments on list `storer` if conditions are correct

        Parameters
        ----------
        storer : list
                 Reserved list to store scraped comments.

        objects : dict
                  Scraped posts obtained from Facebook GraphAPI.

        max_comment_limit : integer or string
                            Determine how many comments you want to retrieve. 
                            Default is `all` that means get all comments.

        GMT : string
              Define GMT that wants to be used with format +{hours}:{minutes}. 
              Example: `+7:00`, `-12:30`

        Returns
        -------
        bool
        """
        if (max_comment_limit is not 'all'):
            for obj in objects['data']:
                obj = _CommentScraper._comment_formalizer(obj, GMT)
                if len(storer) < max_comment_limit:
                    storer.append(obj)
                    condition = True
                else:
                    condition = False
        else:
            for obj in objects['data']:
                obj = _CommentScraper._comment_formalizer(obj, GMT)
                storer.append(obj)
                condition = True
        if len(objects['data']) == 0:
            condition = False
        return condition

    def _post_validation(engine, target_id):
        """
        Validating post is exists or not

        Parameters
        ----------
        engine : facebook.GraphAPI
                 Authenticated API using existing facebook access token.

        target_id : string
                    A facebook post id.
        """
        try:
            return engine.get_object(target_id)
        except:
            logging.error('Post %s not found!' % target_id)
            return None

    def get_comment_data(engine, target_id, add_field=None, remove_field=None, count_limit='all', GMT='+7:00'):
        """
        Scraping comments of post using Facebook GraphAPI based on post ID. Facebook access token is needed.

        Parameters
        ----------
        engine : facebook.GraphAPI
                 Authenticated API using existing facebook access token.

        target_id : string
                    A facebook post id.

        add_field : list, optional
                    See this documentation https://developers.facebook.com/docs/graph-api/reference/comment
                    to know available field options.

        remove_field : list, optional
                       Default fields are `from, story, id, created_time, message, likes, comments, 
                       shares, reactions, status_type, type`. If you want to remove some fields, 
                       just input that fields as list and put to this parameter.

        count_limit : integer or string, optional
                      Determine how many the posts data you want to retrieve. 

        GMT : string
              Define GMT that wants to be used with format +{hours}:{minutes}. 
              Example: `+7:00`, `-12:30`

        """
        comments = []
        max_comment_limit = count_limit

        # set up the fields
        fields = 'from, message, message_tags, created_time, like_count, comment_count, attachment,'
        if (add_field is not None):
            field_adder = ', '.join(add_field)
            fields = '%s, %s' % (fields, field_adder)
        if (remove_field is not None):
            for i in remove_field:
                fields = fields.replace('%s,' % i, '')
        fields = fields.replace(' ','')
        fields = re.sub('\,$','',fields)

        # checking facebook post id is exists
        status = _CommentScraper._post_validation(engine, target_id)
        if (status is not None):

            # requesting comments data from Facebook GraphAPI
            objects = engine.get_connections(id=target_id, connection_name='comments', fields=fields)

            # storing the comments data and navigating to the next page to get more data if conditions are correct
            if (_CommentScraper._comment_storer(storer=comments, objects=objects, GMT=GMT, max_comment_limit=max_comment_limit) is True):
                if len(comments) > 0:
                    while True:
                        logging.info('Scraping post %s comments %i !' % (status['id'], len(comments)))
                        if 'next' in objects['paging']:
                            next_page = objects['paging']['next']
                        else:
                            logging.info('Scraping post %s comments completed! Total : %i' % (status['id'], len(comments)))
                            break
                        objects = requests.get(next_page).json()
                        if (_CommentScraper._comment_storer(storer=comments, objects=objects, GMT=GMT, max_comment_limit=max_comment_limit) is False):
                            logging.info('Scraping post %s comments completed! Total : %i' % (status['id'], len(comments)))
                            break
                else:
                    logging.info('Scraping post %s comments completed! Total : %i' % (status['id'], len(comments)))
            else:
                logging.info('Scraping post %s comments completed! Total : %i' % (status['id'], len(comments)))
        return comments
