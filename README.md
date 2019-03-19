# ImplementationFacebookScraper
Getting data from public Facebook Account/Page/Group and still on progress to scrape possible data! An implementation using mobolic facebook-sdk [https://github.com/mobolic/facebook-sdk] with some custumization like:
* Scraping posts based on days or even how many posts you want to retrieve
* You could set how many groups you want to retrieve while scraping joined groups of user
* You could set how many interest you want to retrieve while scraping interests of user
* Re-structured json result for better understanding

## Getting started
This package allows you to get possible public information data on Facebook using Python 3.7. You need to generate Facebook access token before using this package.

### Prerequisites
I am running on Ubuntu 18.10, Python 3.7. Below are the packages that I use to create this script.
```
pip install git+https://github.com/mobolic/facebook-sdk
Unidecode==1.0.23
python_dateutil==2.8.0
PyYAML==5.1
```

### Installing
* Just use pip to installation
```
pip install git+https://github.com/fchrulk/ImplementationFacebookScraper/
```

### Example
First of all, you need to create yaml file on creds folder. See my-credentials.yaml for an example.

Here it is an example to start using Jupyter Notebook
```
# import package
from ImplementationFacebookScraper.facebook_scraper import FacebookScraper

# call engine
scraper = FacebookScraper()

# authentication using your token
api = scraper.Auth(yaml_file='my-credentials.yaml')

# determine your target id
target_id = '100000092035249'

# scraping basic information of user
account_basic_info = scraper.GetBasicInfoUser(engine=api.engine, target_id=target_id)

# scraping posts of user / page / group
posts = scraper.GetTargetPostsUser(engine=api.engine, target_id=target_id, day_limit=30)

# scraping friends of user 
friends_of_account = scraper.GetUserFriends(engine=api.engine, target_id=target_id, count_limit=25)

# scraping subscribers of user 
subscribers_of_account = scraper.GetSubscriberFriends(engine=api.engine, target_id=target_id, count_limit=25)

# scraping groups of user 
groups_of_account = scraper.GetUserJoinedGroups(engine=api.engine, target_id=target_id, count_limit=25)

# scraping interests of user 
interests_of_account = scraper.GetUserInterests(engine=api.engine, target_id=target_id, count_limit=100)

page_id = '390581294464059'
# scraping page/interest basic information
page_basic_info = scraper.GetBasicInfoPage(engine=api.engine, target_id=page_id)

group_id = '473114992729831'
# scraping group basic information
group_basic_info = scraper.GetBasicInfoGroup(engine=api.engine, target_id=group_id)

```

### Built with
* [**facebook-sdk**](https://github.com/mobolic/facebook-sdk)

## Authors

* **Fachrul Kurniansyah** - *ImplementationFacebookScraper* - [fchrulk](https://github.com/fchrulk)

You can visit my LinkedIn [here](https://www.linkedin.com/in/fchrulk).

Email : [fchrulk@outlook.com]

