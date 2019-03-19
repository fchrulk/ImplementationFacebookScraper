import os as _os
try:
  import facebook as _fb
except:
  _os.system('pip install git+https://github.com/mobolic/facebook-sdk')
  import facebook as _fb

from ._Authentication import _Authentication
from ._UserBasicInfoScraper import _UserBasicInfoScraper
from ._PostScraper import _PostScraper
from ._CommentScraper import _CommentScraper
from ._UserGroupScraper import _UserGroupScraper
from ._UserInterestScraper import _UserInterestScraper
from ._UserFriendScraper import _UserFriendScraper
from ._UserSubscriberScraper import _UserSubscriberScraper

from ._PageBasicInfoScraper import _PageBasicInfoScraper
from ._GroupBasicInfoScraper import _GroupBasicInfoScraper



class FacebookScraper():
    __title__ = 'Implementation FacebookAPI Scraper v3.0'
    __version__ = '1.0.0'
    __author__ = 'fchrulk@outlook.com'
    __doc__ = 'A tool to simplify retrieving data with Facebook GraphAPI. '\
              'Special thanks to Mobolic because it was made generally using '\
              'his open-source Python script on github [https://github.com/mobolic/facebook-sdk]'
    __date__ = '2019'
    
    def Auth(self, yaml_file):
        """
        Try to creating auth using existing access token on selected yaml file on directory `creds/`
        
        Parameter
        ---------
        yaml_file : string
                    Input the name of yaml file. Please place your yaml file on directory `creds/`
                    Example : `fachrul_credentials.yaml`
        """
        return _Authentication(yaml_file)

    def GetBasicInfoUser(self, engine, target_id, add_field=None, remove_field=None):
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
                       Default fields are `from, story, id, created_time, message, likes, comments, 
                       shares, reactions, status_type, type`. If you want to remove some fields, 
                       just input that fields as list and put to this parameter.
        """
        return _UserBasicInfoScraper.get_basic_info(engine, target_id, add_field, remove_field)

    def GetTargetPosts(self, engine, target_id, add_field=None, remove_field=None, day_limit=7, count_limit=None, GMT='+7:00'):
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
        return _PostScraper.get_post_data(engine, target_id, add_field, remove_field, day_limit, count_limit, GMT)

    def GetPostComments(self, engine, target_id, add_field=None, remove_field=None, count_limit='all', GMT='+7:00'):
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
        return _CommentScraper.get_comment_data(engine, target_id, add_field, remove_field, count_limit, GMT)

    def GetUserJoinedGroups(self, engine, target_id, add_field=None, remove_field=None, count_limit=25, GMT='+7:00'):
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
        return _UserGroupScraper.get_user_joined_group(engine, target_id, add_field, remove_field, count_limit, GMT)

    def GetUserInterests(self, engine, target_id, add_field=None, remove_field=None, count_limit=25, GMT='+7:00'):
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
        return _UserInterestScraper.get_user_interest(engine, target_id, add_field, remove_field, count_limit, GMT)

    def GetUserFriends(self, engine, target_id, add_field=None, remove_field=None, count_limit=10000, subscriber_count=False):
        """
        Scraping friends of target using Facebook GraphAPI based on user ID. Facebook access token is needed.

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
                      Determine how many the friends data you want to retrieve. 

        subscriber_count : boolean, optional
                           Default is False. Whether to get count of subscribers on each friends or not.
                           (will takes more time, better not get it)
        """
        return _UserFriendScraper.get_friend_data(engine, target_id, add_field, remove_field, count_limit)

    def GetSubscriberFriends(self, engine, target_id, add_field=None, remove_field=None, count_limit=None, friend_count=False):
        """
        Scraping friends of target using Facebook GraphAPI based on user ID. Facebook access token is needed.

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
                      Determine how many the friends data you want to retrieve. 

        friend_count : boolean, optional
                       Default is False. Whether to get count of friends on each friends or not.
                       (will takes more time, better not get it)
        """
        return _UserSubscriberScraper.get_subscriber_data(engine, target_id, add_field, remove_field, count_limit, friend_count)

    def GetBasicInfoPage(self, engine, target_id, add_field=None, remove_field=None):
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
                       Default fields are `from, story, id, created_time, message, likes, comments, 
                       shares, reactions, status_type, type`. If you want to remove some fields, 
                       just input that fields as list and put to this parameter.
        """
        return _PageBasicInfoScraper.get_basic_info(engine, target_id, add_field, remove_field)

    def GetBasicInfoGroup(self, engine, target_id, add_field=None, remove_field=None, GMT='+7:00'):
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
                       Default fields are `from, story, id, created_time, message, likes, comments, 
                       shares, reactions, status_type, type`. If you want to remove some fields, 
                       just input that fields as list and put to this parameter.
        """
        return _GroupBasicInfoScraper.get_basic_info(engine, target_id, add_field, remove_field, GMT)
