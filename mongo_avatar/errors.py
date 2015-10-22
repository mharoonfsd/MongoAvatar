from pymongo import errors

class Error(Exception):
    pass

class DatabaseConfigurationError(Error):
    
    def __init__(self):
        self.type = "DatabaseConfigurationError"
        self.msg = "Connection to database failed!"
    
    def __str__(self):
        return repr(self.msg)
    
    
class MultipleObjectsReturnedError(Error):
    
    def __init__(self):
        self.type = "MultipleObjectsReturnedError"
        self.msg = "Query returned more than one objects!"
    
    def __str__(self):
        return repr(self.msg)
    
    
class ObjectDoesNotExistError(Error):
    
    def __init__(self):
        self.type = "ObjectDoesNotExistError"
        self.msg = "Quried object does not exist!"
    
    def __str__(self):
        return repr(self.msg)
    
    
class NoCollectionSpecifiedError(Error):
    
    def __init__(self):
        self.type = "NoCollectionSpecifiedError"
        self.msg = "No collection specified for query!"
    
    def __str__(self):
        return repr(self.msg)
    
    
class NonExistentDatabaseError(Error):
    
    def __init__(self):
        self.type = "NonExistentDatabaseError"
        self.msg = "Database specified for query doesnot exist!"
    
    def __str__(self):
        return repr(self.msg)
    

class InvalidQueryError(Error):
    
    def __init__(self):
        self.type = "InvalidQueryError"
        self.msg = "Invalid arguments in query."
    
    def __str__(self):
        return repr(self.msg)
 
    
class InvalidCreateQueryError(Error):
    
    def __init__(self, argument):
        self.type = "InvalidQueryError"
        self.msg = 'Invalid conditional argument "' + argument + '" in create query.'
    
    def __str__(self):
        return repr(self.msg)
    

class InvalidOrderingArgumentError(Error):
    
    def __init__(self):
        self.type = "InvalidOrderingArgumentError"
        self.msg = 'Invalid ordering argument in query.'
    
    def __str__(self):
        return repr(self.msg)
        
        
# Attaching Pymongo Errors
        
DuplicateKeyError = errors.DuplicateKeyError
InvalidDocumentError = errors.InvalidDocument
BulkWriteError = errors.BulkWriteError
CollectionInvalidError = errors.CollectionInvalid
ConfigurationError = errors.ConfigurationError
ConnectionFailureError = errors.ConnectionFailure
CursorNotFoundError = errors.CursorNotFound
DocumentTooLargeError = errors.DocumentTooLarge
ExceededMaxWaitersError = errors.ExceededMaxWaiters
ExecutionTimeoutError = errors.ExecutionTimeout
InvalidNameError = errors.InvalidName
InvalidOperationError = errors.InvalidOperation
InvalidURIError = errors.InvalidURI
NetworkTimeoutError = errors.NetworkTimeout
NotMasterError = errors.NotMasterError
OperationFailureError = errors.OperationFailure
PyMongoError = errors.PyMongoError
ServerSelectionTimeoutError = errors.ServerSelectionTimeoutError
WTimeoutError = errors.WTimeoutError
WriteConcernError = errors.WriteConcernError
WriteError = errors.WriteError
