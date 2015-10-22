from mongo_avatar.db import MONGO_CONNECTIONS
from mongo_avatar.query import Objects
from mongo_avatar import errors
from datetime import datetime


class MongoModel(object):
    
    def __init__(self, *args, **kwargs):
        
        class Meta: pass
        self._meta = Meta()
        try:
            setattr(self, '__fields__', self.getfields(args[2]))
        except IndexError:
            pass
        except KeyError:
            pass
        try:
            setattr(self._meta, 'db', MONGO_CONNECTIONS.get('default'))
        except AttributeError:
            pass
        try:
            setattr(self._meta, 'app', args[2]['__module__'].split('.')[0])
        except IndexError:
            pass
        except KeyError:
            pass
        try:
            if not hasattr(args[2].get('Meta'), 'collection'):
                setattr(self._meta, 'collection', self._meta.app.lower() + '_' + args[0].lower())
            else:
                setattr(self._meta, 'collection', getattr(args[2].get('Meta'), 'collection'))
        except IndexError:
            pass
        except AttributeError:
            pass
        self.sync = True
        try:
            if hasattr(args[2].get('Meta'), 'sync'):
                if getattr(args[2].get('Meta'), 'sync') == True:
                    self.sync = True
                else: self.sync = False
            else:
                pass
        except IndexError:
            pass
        try:    
            self._meta.__fields__ = self.getfields(args[2])
            self.model_name = args[0]
        except IndexError:
            pass
        except KeyError:
            pass
        self.objects = Objects(model=self)
        self.errors = errors
        
    def __getitem__(self, item):
        return self.__fields__[item]
    
    def __repr__(self):
        if hasattr(self, "__unicode__"):
            return "<" + self.model_name + " object: " + self.__unicode__() + ">"
        else:
            return "<" + self.model_name + " object: " + str(self._id) + ">"
    
    def save(self):
        fields = self.__fields__
        _update = {}
        for item in dir(self):
            if not item.startswith('__')\
            and not item.endswith('__'):
                if item not in _update.keys()\
                and type(getattr(self, item, None)) in [bool, str, int, float, list, unicode, dict, datetime, set]\
                and item is not 'model_name'\
                and item is not 'sync':
                    _update.update({item: getattr(self, item)})
            else:
                continue
        self._meta.db[self._meta.collection].update_one({"_id": self._id}, {"$set": _update})
        return self
    
    def delete(self):
        self._meta.db[self._meta.collection].remove({"_id": self._id})
        del(self)
        return None
    
    def getfields(self, all_fields):
        fields = {}
        for item in all_fields.keys():
            if item.startswith('__')\
            and item.endswith('__')\
            or item == 'Meta'\
            or item=='delete':
                continue
            else:
                fields.update({item: all_fields[item]})
        return fields
    
    
class MongoField(object):
    
    def __init__(self, unique=False, null=False, default=None, db_index=False):
        self.options = {
            'unique': unique, 
            'null': null, 
            'default': default,
            'db_index': db_index,
        }
        
        
class MongoForeignKey(object):
    pass


class MongoManyToOneField(object):
    pass


class MongoManyToManyField(object):
    pass


MongoModel = MongoModel()
