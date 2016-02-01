from mongo_avatar.db import MONGO_CONNECTIONS
from mongo_avatar.errors import *
import inspect, re
from copy import copy
from pymongo import errors
import random


REPR_OUTPUT_SIZE = 20

class Query(object):
    
    def interprete(self, database, collection, fields, arguments):
        current_frame = inspect.currentframe()
        caller_frame = inspect.getouterframes(current_frame, 2)
        caller =  caller_frame[1][3]
        criteria = {}
        for key in arguments.keys():
            if '__' in key:
                _key = key.split('__')[0]
                _filter = key.split('__')[1]
                if _filter == 'exact': arguments.update({_key: arguments.get(key)})
                elif _filter == 'gte': arguments.update({_key: {'$gte': arguments.get(key)}})
                elif _filter == 'lte': arguments.update({_key: {'$lte': arguments.get(key)}})
                elif _filter == 'iexact': arguments.update({_key: re.compile(arguments.get(key), re.IGNORECASE)})
                elif _filter == 'lt': arguments.update({_key: {'$lt': arguments.get(key)}})
                elif _filter == 'gt': arguments.update({_key: {'$gt': arguments.get(key)}})
                elif _filter == 'contains': 
                    if type(arguments.get(key)) == dict:
                        arguments.update({_key: arguments.get(key)})
                    else:
                        arguments.update({_key: re.compile('.*' + str(arguments.get(key)) + '.*')})
                elif _filter == 'exists': arguments.update({_key: {'$exists': arguments.get(key)}})
                else: arguments.update({_key: arguments.get(key)})
                arguments.pop(key)
        for key in arguments.keys():
            if key not in criteria:
                criteria.update({key: arguments[key]})
        for key in fields.keys():
            if key not in criteria and fields[key].options.get('default') not in [None, False]:
                criteria.update({key: fields[key].options.get('default')})
        if caller == 'create':
            try:
                cursor = database[collection].find_one({'_id': database[collection].insert_one(criteria).inserted_id})
            except errors.InvalidDocument as err:
                invalid_argument = re.search(r"\$\w+", err.message)
                if invalid_argument:
                    raise InvalidCreateQueryError(invalid_argument.group()[1:])
                else:
                    raise err
            return cursor
        elif caller == 'get':
            for item in criteria.keys():
                if item not in arguments.keys():
                    criteria.pop(item)
            cursor = database[collection].find(criteria)
            if cursor.count() == 0:
                raise ObjectDoesNotExistError
            elif cursor.count() > 1:
                raise MultipleObjectsReturnedError
            else:
                cursor = database[collection].find_one({'_id': cursor[0].get('_id')})
                return cursor
        elif caller == 'filter':
            for item in criteria.keys():
                if item not in arguments.keys():
                    criteria.pop(item)
            print criteria
            cursor = database[collection].find(criteria)
            return cursor
        elif caller == 'all':
            cursor = database[collection].find()
            return cursor
        elif caller == 'exclude':
            for item in criteria.keys():
                if item not in arguments.keys():
                    criteria.pop(item)
            cursor = database[collection].find(criteria)
            return cursor
        elif caller == 'delete':
            for item in criteria.keys():
                if item not in arguments.keys():
                    criteria.pop(item)
            cursor = database[collection].remove(criteria)
            if cursor:
                return cursor
            else:
                return []
        else:
            raise InvalidQueryError
        
        
class Queryset(object):
    
    def __init__(self, model, query, *args, **kwargs):
        self.query = query
        self.model = model
        self.query_object = Query()
        self.ordering = None
        self.indexes = range(self.query.count())
    
    def __repr__(self):
        self.indexes = range(self.query.count())
        data = self.__getslice__(0, REPR_OUTPUT_SIZE)
        if self.query.count() > REPR_OUTPUT_SIZE:
            data[-1] = "...(remaining elements truncated)..."
        return repr(data)
    
    def __len__(self):
        return self.query.count()
    
    def __iter__(self):
        self.index = 0
        self.end = self.query.count() - 1
        self.indexes = range(self.query.count())
        if self.ordering == '?':
            random.shuffle(self.indexes)
        elif type(self.ordering) == str\
            and (self.ordering in self.model.__fields__\
                or (self.ordering.startswith('-')\
                and self.ordering[1:] in self.model.__fields__)):
            if self.ordering.startswith('-'):
                self.query.sort(self.ordering[1:], -1)
            else:
                self.query.sort(self.ordering, 1)
        elif self.ordering is None:
            pass
        else:
            raise InvalidOrderingArgumentError
        return self
    
    def next(self):
        try:
            item = self.__getitem__(self.indexes[self.index])
            self.index += 1
            return item
        except IndexError:
            self.index = self.query.count() - 1
            raise StopIteration
    
    def __getitem__(self, idx):
        model = copy(self.model)
        for key in self.query[idx].keys():
            setattr(model, key, self.query[idx].get(key))
        return model
    
    def __getslice__(self, start=0, end=None, step=1):
        if not end or (end > self.query.count()):
            end = self.query.count()
        if not start or (start > self.query.count()):
            pass
        slic = []
        for i in range(start, end, step):
            model = self.__getitem__(self.indexes[i])
            slic.append(model)
        return slic
    
    def order_by(self, parameter):
        self.ordering = parameter
        return copy(self)
    
    def filter(self, *args, **kwargs):
        query = copy(self.query)
        if self.ordering in [None, False]:
            criteria = query._Cursor__query_spec()
        elif query._Cursor__query_spec().get('$query'):
            criteria = query._Cursor__query_spec().get('$query')
        else:
            criteria = query._Cursor__query_spec()
        for item in criteria:
            kwargs.update({item: criteria.get(item)})
        new_query = self.query_object.interprete(
            self.model._meta.db, 
            self.model._meta.collection, 
            self.model.__fields__, 
            kwargs
        )
        self_copy = copy(self)
        self_copy.query = new_query
        return self_copy
    
    def exclude(self, *args, **kwargs):
        for item in kwargs.keys():
            if type(kwargs.get(item)) == str:
                kwargs[item] = {'$not': re.compile('.*' + str(kwargs[item]) + '.*')}
            elif '__' in item:
                _item, _key = item.split('__')[0], item.split('__')[1]
                kwargs.update({_item: {'$not' : {'$' + _key: kwargs[item]}}})
                kwargs.pop(item)
            else:
                kwargs[item] = {'$not': kwargs[item]}
        query = copy(self.query)
        if self.ordering in [None, False]:
            criteria = query._Cursor__query_spec()
        elif query._Cursor__query_spec().get('$query'):
            criteria = query._Cursor__query_spec().get('$query')
        else:
            criteria = query._Cursor__query_spec()
        for item in criteria:
            kwargs.update({item: criteria.get(item)})
        new_query = self.query_object.interprete(
            self.model._meta.db, 
            self.model._meta.collection, 
            self.model.__fields__, 
            kwargs
        )
        self_copy = copy(self)
        self_copy.query = new_query
        return self_copy
    
    def delete(self):
        query = copy(self.query)
        if self.ordering in [None, False]:
            criteria = query._Cursor__query_spec()
        elif query._Cursor__query_spec().get('$query'):
            criteria = query._Cursor__query_spec().get('$query')
        else:
            criteria = query._Cursor__query_spec()
        query = self.query_object.interprete(
            self.model._meta.db, 
            self.model._meta.collection, 
            self.model.__fields__, 
            criteria
        )
        del(self)
        return None
        
            
class Objects(object):
    
    def __init__(self, *args, **kwargs):
        attributes = kwargs.get('attributes')
        self.query = Query() 
        self.model = kwargs.get('model')
        dir(self.model)
        if self.model:
            self.__fields__ = getattr(self.model._meta, '__fields__', False)
            self._meta = getattr(self.model, '_meta', False)
    
    def create(self, *args, **kwargs):
        query = self.query.interprete(
            self._meta.db, 
            self._meta.collection, 
            self.__fields__, 
            kwargs
        )
        model = copy(self.model)
        for item in query.keys():
            setattr(model, item, query[item])
        return model
    
    def get(self, *args, **kwargs):
        query = self.query.interprete(
            self._meta.db, 
            self._meta.collection, 
            self.__fields__, 
            kwargs
        )
        model = copy(self.model)
        for item in query.keys():
            setattr(model, item, query[item])
        return model
    
    def filter(self, *args, **kwargs):
        query = self.query.interprete(
            self._meta.db, 
            self._meta.collection, 
            self.__fields__, 
            kwargs
        )
        queryset = copy(Queryset(self.model, query))
        return queryset
    
    def all(self):
        query = self.query.interprete(
            self._meta.db, 
            self._meta.collection, 
            self.__fields__, 
            {}
        )
        queryset = copy(Queryset(self.model, query))
        return queryset
    
    def exclude(self, *args, **kwargs):
        for item in kwargs:
            if type(kwargs.get(item)) == str:
                kwargs[item] = {'$not': re.compile('.*' + str(kwargs[item]) + '.*')}
            else:
                kwargs[item] = {'$not': kwargs[item]}
        query = self.query.interprete(
            self._meta.db, 
            self._meta.collection, 
            self.__fields__, 
            kwargs
        )
        queryset = copy(Queryset(self.model, query))
        return queryset
    
    def using(self, database):
        try:
            self._meta.db = MONGO_CONNECTIONS[database]
            self.model._meta.db = MONGO_CONNECTIONS[database]
            return copy(self)
        except KeyError:
            raise NonExistentDatabaseError
    
