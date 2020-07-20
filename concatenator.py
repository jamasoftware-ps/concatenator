import configparser
import datetime
import logging
import os
import sys

from py_jama_rest_client.client import JamaClient, APIException

logger = logging.getLogger(__name__)


def do_work():
    # Gather script inputs from config
    project_id = None
    set_id = None
    set_prefix_field = None
    item_target_field = None
    try:
        project_id = config.getint('SCRIPT_SETTINGS', 'project_id')
        set_id = config.getint('SCRIPT_SETTINGS', 'set_api_id')
        set_prefix_field = config.get('SCRIPT_SETTINGS', 'set_prefix_field').strip()
        item_target_field = config.get('SCRIPT_SETTINGS', 'item_target_field').strip()
    except configparser.Error as config_error:
        logger.error("Unable to parse SCRIPT_SETTINGS because: {} Please check settings and try again."
                     .format(str(config_error)))
        exit(1)

    # Get project items
    logger.info("Fetching project: {}".format(str(project_id)))
    try:
        project_items = jama_client.get_items(project_id)
    except APIException as api_error:
        logger.error("Unable to fetch project {}. Aborting.".format(str(project_id)))
        logger.error(api_error)
        return

    # Get Set item from project item list
    set_item = None
    try:
        for item in project_items:
            if item.get('id') == set_id:
                set_item = item
                break
    except Exception as ex:
        logger.error("Unable to locate set item {}. Aborting.".format(str(set_id)))
        return

    if set_item is None:
        logger.error("Unable to locate set item {}. Aborting.".format(str(set_id)))
        return

    # Get the prefix.
    prefix = None
    if set_prefix_field in set_item.get('fields'):
        prefix = set_item.get('fields').get(set_prefix_field)

    if prefix is None:
        prefix = set_item.get('fields').get('{}${}'.format(set_prefix_field, str(set_item.get('itemType'))))

    if prefix is None:
        logger.error("Unable to locate prefix field from set {}".format(str(set_id)))
    else:
        logger.info("Located set prefix: {}".format(prefix))

    # Process each item in this set
    set_sequence = set_item.get('location').get('sequence')

    for item in project_items:
        if str(item.get('location').get('sequence')).startswith(set_sequence) and item is not set_item:
            # Process item
            item_fields = item.get('fields')
            field_name = item_target_field
            # Determine if the target field is present in the item payload.
            if item_target_field in item_fields:
                pass
            elif '{}${}'.format(item_target_field, item.get('itemType')) in item_fields:
                field_name = '{}${}'.format(item_target_field, item.get('itemType'))
            else:
                # Field not found.  We will skip this one.
                logger.error("Unable to locate target field {} in item {}".format(item_target_field, item.get('id')))
                continue

            # Do the concatenation
            concatenated_field = '{}{}'.format(prefix, item_fields.get(field_name))

            # Patch the item
            try:
                patch = {
                    'op': 'replace',
                    'path': '/fields/{}'.format(field_name),
                    'value': concatenated_field
                }
                patches = [patch]
                jama_client.patch_item(item.get('id'), patches)
            except APIException as api_error:
                logger.error("Unable to patch item {}".format(item.get('id')))
                logger.error(api_error)
                continue

            # Log success of item patch.
            logger.info("Item {} updated with: {}".format(item.get('id'), concatenated_field))


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
