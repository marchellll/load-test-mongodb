import os

DEFAULTS = {'DB_NAME': 'wagely',
            'CLUSTER_URL': f'mongodb+srv://marchell:XXXXXXXXXX@poc.w9axy.mongodb.net/test?retryWrites=true&w=majority',
            'INSERT_WEIGHT': 10000,
            'AGG_PIPE_WEIGHT': 10}



def init_defaults_from_env():
    for key in DEFAULTS.keys():
        value = os.environ.get(key)
        if value:
            DEFAULTS[key] = value


# get the settings from the environment variables
init_defaults_from_env()
