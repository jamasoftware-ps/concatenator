import configparser
import datetime
import logging
import os
import sys

from py_jama_rest_client.client import JamaClient

logger = logging.getLogger(__name__)


def do_work():
    pass


def init_logging():
    try:
        os.makedirs('logs')
    except FileExistsError:
        pass
    current_date_time = datetime.datetime.now().strftime("%Y-%m-%d %H_%M_%S")
    log_file = 'logs/concatenator_' + str(current_date_time) + '.log'
    logging.basicConfig(filename=log_file, level=logging.INFO)
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))


def parse_config():
    if len(sys.argv) != 2:
        logger.error("Incorrect number of arguments supplied.  Expecting path to config file as only argument.")
        exit(1)
    current_dir = os.path.dirname(__file__)
    path_to_config = sys.argv[1]
    if not os.path.isabs(path_to_config):
        path_to_config = os.path.join(current_dir, path_to_config)

    # Parse config file.
    configuration = configparser.ConfigParser()
    configuration.read_file(open(path_to_config))
    return configuration


def create_jama_client():
    url = None
    user_id = None
    user_secret = None
    oauth = None
    try:
        url = config.get('CLIENT_SETTINGS', 'jama_connect_url').strip()
        # Clenup URL field
        while url.endswith('/') and url != 'https://' and url != 'http://':
            url = url[0:len(url) - 1]
        # If http or https method not specified in the url then add it now.
        if not (url.startswith('https://') or url.startswith('http://')):
            url = 'https://' + url
        oauth = config.getboolean('CLIENT_SETTINGS', 'oauth')
        user_id = config.get('CLIENT_SETTINGS', 'user_id').strip()
        user_secret = config.get('CLIENT_SETTINGS', 'user_secret').strip()
    except configparser.Error as config_error:
        logger.error("Unable to parse CLIENT_SETTINGS from config file because: {}, "
                     "Please check config file for errors and try again."
                     .format(str(config_error)))
        exit(1)

    return JamaClient(url, (user_id, user_secret), oauth=oauth)


# Execute this as a script.
if __name__ == "__main__":
    # Setup logging
    init_logging()

    # Get Config File Path
    config = parse_config()

    # Create Jama Client
    jama_client = create_jama_client()

    # Begin business logic
    do_work()

    logger.info("Done.")
