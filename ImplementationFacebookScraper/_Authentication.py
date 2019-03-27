import logging
import facebook
import yaml
import os

def api_logger(yaml_file):
    """
    Setting up logger
    """
    logger = logging.getLogger()
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')

    # Setup file handler
    if not os.path.exists('logger/'):
        os.makedirs('logger')

    fhandler  = logging.FileHandler('logger/%s.log' % yaml_file.replace('.yaml',''))
    fhandler.setLevel(logging.DEBUG)
    fhandler.setFormatter(formatter)

    # Configure stream handler for the cells
    chandler = logging.StreamHandler()
    chandler.setLevel(logging.INFO)
    chandler.setFormatter(formatter)

    # Add both handlers
    logger.addHandler(fhandler)
    logger.addHandler(chandler)
    logger.setLevel(logging.INFO)

    # Show the handlers
    logger.handlers
    return logger

class _Authentication():
    def __init__(self, yaml_file, source_path_creds='creds/'):
        """
        Try to creating auth using existing access token on selected yaml file on directory `creds/`
        
        Parameter
        ---------
        yaml_file : string
                    Input the name of yaml file. Please place your yaml file on directory `creds/`
                    Example : `fachrul_credentials.yaml`
        """
        self.logger = api_logger(yaml_file)
        creds = self._load_credential(yaml_file=yaml_file, source_path=source_path_creds)
        logging.info('Scraper using worker : %s' % creds['name'])
        self.engine = self._auth(token=creds['token'])
        self.worker_info = self._worker_info()
    
    def _load_credential(self, yaml_file, source_path='creds/'):
        """
        Load credentials on yaml file        
        """
        return yaml.load(open('%s%s' % (source_path, yaml_file)).read())

    def _auth(self, token):
        """
        Connect to Facebook GraphAPI
        """
        return facebook.GraphAPI(access_token=token, version='3.0')
    
    def _worker_info(self):
        """
        Get worker information
        """
        batched_requests = '[{"method":"GET","relative_url":"me"},{"method":"GET","relative_url":"me/"}]'
        info = self.engine.request("", post_args = {"batch":batched_requests})
        return eval(info[0]['body'])
        
