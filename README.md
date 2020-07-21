# concatenator
This script will concatenate a prefix found in a custom field on a Jama Set item with a field on each item in the set, 
and store the result into a field on the item.


# Installation
This section contains information on how to install the required dependencies for this script.

## Pre-Requisites
* [Python 3.7+](https://www.python.org/downloads/release/python-377/) 

* [py-jama-rest-client](https://pypi.org/project/py-jama-rest-client/)
        
        ```bash
        pip install --user py-jama-rest-client
        ```

* Enable the REST API on your Jama Connect instance

# Usage
This section contains information on configuration and execution the script.

## Configuration
Before the script can begin, a config file must be created.  The config file is
structured in a .ini file format. A template config.ini file is included.

#### Client Settings:
This section contains settings related to connecting to your Jama Connect REST API.

* jama_connect_url: URL to a Jama Connect instance

* oauth: setting this value to 'false' will instruct the client to authenticate via basic authentication.  Setting this 
value to 'true' instructs the client to use OAuth authentication protocols

* user_id: Either a username or clientID if using OAuth

* user_secret: Either a password or client_secret if using OAuth

#### Script Settings:

* project_id: API id of the project

* set_api_id: API id of the set

* set_prefix_field: Unique field name of the prefix field on the set item

* item_target_field: Unique field name of the field to concatenate the set prefix
and store the result


## Running the script

1) Open a terminal to the project directory.
2) Enter the following command into your terminal (Note that the script accepts one parameter and that is the path to
the config file created above):  
   ```bash 
   python harm-severity-updater.py config.ini
   ```

## Output
Execution logs will be output to the terminal as well as output to a log file in the logs/ folder located next to the 
script.