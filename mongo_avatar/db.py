from pymongo import MongoClient
from django.conf import settings
from mongo_avatar.errors import DatabaseConfigurationError



class Connections(object):
    
    @classmethod    
    def connect(self, *args, **kwargs):
        if kwargs.get('MONGO_CONNECTIONS'):
            connections = {}
            MONGO_CONNECTIONS = kwargs.get('MONGO_CONNECTIONS')
            for cred_key in MONGO_CONNECTIONS:
                try:
                    client = MongoClient(
                        MONGO_CONNECTIONS[cred_key].get('HOST'),
                        int(MONGO_CONNECTIONS[cred_key].get('PORT')),
                    )
                    if MONGO_CONNECTIONS[cred_key].get('USER') \
                    and MONGO_CONNECTIONS[cred_key].get('PASSWORD'):
                        client[MONGO_CONNECTIONS[cred_key].get('NAME')].authenticate(
                            MONGO_CONNECTIONS[cred_key].get('USER'),
                            MONGO_CONNECTIONS[cred_key].get('PASSWORD'),
                        )
                    connections.update({cred_key: client})
                except Exception as err:
                    continue
            return connections
        elif hasattr(settings, 'MONGO_CONNECTIONS'):
            MONGO_CONNECTIONS = settings.MONGO_CONNECTIONS
            connections = {}
            for cred_key in MONGO_CONNECTIONS:
                try:
                    client = MongoClient(
                        MONGO_CONNECTIONS[cred_key].get('HOST'),
                        int(MONGO_CONNECTIONS[cred_key].get('PORT')),
                    )
                    if MONGO_CONNECTIONS[cred_key].get('USER') \
                    and MONGO_CONNECTIONS[cred_key].get('PASSWORD'):
                        client[MONGO_CONNECTIONS[cred_key].get('NAME')].authenticate(
                            MONGO_CONNECTIONS[cred_key].get('USER'),
                            MONGO_CONNECTIONS[cred_key].get('PASSWORD'),
                        )
                    db = client[MONGO_CONNECTIONS[cred_key].get('NAME')]
                    connections.update({cred_key: db})
                except Exception as err:
                    continue
            return connections
        else:
            return []


Connections = Connections()
if hasattr(settings, 'MONGO_CONNECTIONS'):
    try:
        MONGO_CONNECTIONS = Connections.connect()
    except Exception as err:
        raise err
else:
    raise DatabaseConfigurationError
