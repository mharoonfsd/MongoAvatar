from django.core.management.base import BaseCommand
from pymongo import MongoClient, errors
from django.conf import settings
from optparse import make_option
from mongo_avatar.helpers import __import__
from mongo_avatar.models import MongoModel
            

INSTALLED_APPS = settings.INSTALLED_APPS
for app in INSTALLED_APPS:
    app = app.split('.')[0]
    imported_app = __import__(app)
    exec(app + ' = imported_app')

if hasattr(settings, 'MONGO_CONNECTIONS'):
    try:
        MONGO_SERVER = settings.MONGO_CONNECTIONS.get('default')
        client = MongoClient(
                MONGO_SERVER.get('HOST'),
                int(MONGO_SERVER.get('PORT')),
            )
    except Exception as err:
        raise err
else:
    pass

if MONGO_SERVER:
    class Command(BaseCommand):
        args = '<argumentname atgumentvalue ...>'
        help = "Sync Mongo Models"
        can_import_settings = True
        option_list = BaseCommand.option_list + (
            make_option('--database',
                help='Specify database to sync'),
            )
        def connect(self, database):
            MONGO_SERVER = settings.MONGO_CONNECTIONS.get(database)
            try:
                client = MongoClient(
                    MONGO_SERVER.get('HOST'),
                    int(MONGO_SERVER.get('PORT')),
                )
                if MONGO_SERVER.get('USER') and MONGO_SERVER.get('PASSWORD'):
                    client[MONGO_SERVER.get('NAME')].authenticate(
                        MONGO_SERVER.get('USER'),
                        MONGO_SERVER.get('PASSWORD'),
                    )
                db = client[MONGO_SERVER.get('NAME')]
                return db
            except Exception as err:
                raise err
        
        def handle(self, *args, **options):
            database = self.connect(options.get('database', False) or 'default')
            print '- Syncing collections...'
            for app in INSTALLED_APPS:
                app_name = app
                try:
                    models = eval(app + '.models')
                except AttributeError as err:
                    models = None
                if models:
                    for item in dir(models):
                        app_name = app_name + '_'
                        if type(eval('models.' + item)) == type(MongoModel) and item is not 'MongoModel':
                            model = eval('models.' + item)
                            if hasattr(model._meta, 'collection') and type(getattr(model._meta, 'collection', False)) == type('str'):
                                app_name = ''
                                item = getattr(model._meta, 'collection')
                            print "- Creating Collection " + app_name + item.lower()
                            database[app_name + item.lower()].delete_one({"_id": database[app_name + item.lower()].insert_one({"temp": 1}).inserted_id})
                            for field in model.__fields__:
                                if model[field].options['unique']:
                                    print "- Creating unique index " + app_name + item.lower() + '_' + field + "_unique"
                                    try:
                                        database[app_name + item.lower()].delete_one({"_id": database[app_name + item.lower()].insert_one({"temp": 1}).inserted_id})
                                        database[app_name + item.lower()].drop_index(app_name + item.lower() + '_' + field + "_unique")
                                        database[app_name + item.lower()].ensure_index(app_name + field, name=app_name + item.lower() + '_' + field + "_unique", unique=True, drop_dups=True)
                                    except errors.OperationFailure:
                                        database[app_name + item.lower()].delete_one({"_id": database[app_name + item.lower()].insert_one({"temp": 1}).inserted_id})
                                        database[app_name + item.lower()].ensure_index(app_name + field, name=app_name +  item.lower() + '_' + field + "_unique", unique=True, drop_dups=True)
                                if model[field].options['db_index']:
                                    print "- Creating index "+ app_name + item.lower() + '_' + field + "_index"
                                    try:
                                        database[app_name + item.lower()].delete_one({"_id": database[app_name + item.lower()].insert_one({"temp": 1}).inserted_id})
                                        database[app_name + item.lower()].drop_index(app_name + item.lower() + '_' + field + "_index")
                                        database[app_name + item.lower()].ensure_index(app_name + field, name=app_name + item.lower() + '_' + field + "_index")
                                    except errors.OperationFailure:
                                        database[app_name + item.lower()].delete_one({"_id": database[app_name + item.lower()].insert_one({"temp": 1}).inserted_id})
                                        database[app_name + item.lower()].ensure_index(app_name + field, name=app_name +  item.lower() + '_' + field + "_index")
