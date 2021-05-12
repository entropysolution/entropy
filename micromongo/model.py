# -*- coding: utf-8 -*-
from __future__ import absolute_import

import re
import six
import sys
import copy
import logging
import datetime
from .options import _Options
from bson import DBRef, ObjectId
from bson.errors import InvalidId
from .collection import DummyCollection
from pymongo import MongoClient as Connection
from marshmallow import Schema, fields, missing, validate
from pymongo.errors import DuplicateKeyError

if sys.version_info[0] >= 3:
    unicode = str

log = logging.getLogger('minimongo.model')

class ExtSchema(Schema):
    _mapping = {}
    @classmethod
    def getmap(cls, field_name, target, schema_fields):
        schema_field = schema_fields[field_name]
        mapping = schema_field.metadata.get('mapping')
        v = target
        if mapping is None:
            mapping = field_name
        for el in mapping.split('.'):
            if el[-2:] in ('{}', '[]'):
                default = {} if el[-2:] == '{}' else []
                v = v.get(el[:-2], default)
            else:
                v = v.get(el, schema_field.default if schema_field.default != missing else None)
                if schema_field.__class__.__name__ != 'Nested':
                    try:
                        v = schema_field.deserialize(v)
                    except:
                        pass
        if schema_field.__class__.__name__ == 'Nested':
            if schema_field.many:
                v = [schema_field.nested.getmaps(sv) for sv in v]
            else:
                v = schema_field.nested.getmaps(v)
        return v

    @classmethod
    def getmaps(cls, target):
        schema_fields = cls().fields
        return {field: cls.getmap(field, target, schema_fields) for field, field_prop in schema_fields.items()}

    @classmethod
    def postmap(cls, input):
        output = {}
        schema_fields = cls().fields
        input = cls().load(input)
        if input.errors != {}:
            raise ValueError('Parsing error: %s' % (input.errors))
        for field_name, field_value in input.data.items():
            schema_field = schema_fields[field_name]
            mapping = schema_field.metadata.get('mapping')
            if mapping is None:
                mapping = field_name
            v = output
            for el in mapping.split('.'):
                if el[-2:] in ['{}', '[]']:
                    default = {} if el[-2:] == '{}' else []
                    v[el[:-2]] = v.get(el[:-2], default)
                    v = v[el[:-2]]
                else:
                    if schema_field.__class__.__name__ == 'Nested':
                        if schema_field.many:
                            field_value = [schema_field.nested.postmap(sv) for sv in field_value]
                        else:
                            field_value = schema_field.nested.postmap(field_value)
                    v[el] = field_value
        return output 


class ObjectIdField(fields.String):
    """ObjectId field."""

    default_error_messages = {"invalid_objectid": "Not a valid ObjectId."}

    def _validated(self, value):
        """Format the value or raise a :exc:`ValidationError` if an error occurs."""
        if value is None:
            return None
        if isinstance(value, ObjectId):
            return value
        try:
            return ObjectId(value)
        except (ValueError, AttributeError, TypeError, InvalidId):
            self.fail('invalid_objectid')

    def _deserialize(self, value, attr, data, **kwargs):
        return self._validated(value)
fields.ObjectId = ObjectIdField

class AwareDateTimeObjectField(fields.String):
    """datetime field."""

    default_error_messages = {"invalid_datetime": "Not a valid datetime object.", "naive_datetime": "datetime is not timezone aware"}

    def _validated(self, value):
        """Format the value or raise a :exc:`ValidationError` if an error occurs."""
        if value is None:
            return None
        if isinstance(value, datetime.datetime):
            if value.tzinfo is None:
                return self.fail('naive_datetime')
            return value
        self.fail('invalid_datetime')

    def _deserialize(self, value, attr, data, **kwargs):
        return self._validated(value)
fields.AwareDateTimeObject = AwareDateTimeObjectField

class CoordinatesField(fields.Field): # [Lat, Lng]
    default_error_messages = {"invalid_type": "Invalid data type"}
    def _deserialize(self, value, attr, data, **kwargs):
        if isinstance(value, list) or isinstance(value, tuple) and len(value) == 2:
            try:
                return [round(float(value[0]), 7), round(float(value[0]), 7)]
            except:
                self.fail('invalid_type')
        else:
            self.fail('invalid_type')
fields.Coordinates = CoordinatesField


class ModelBase(type):
    """Metaclass for all models.

    .. todo:: add Meta inheritance -- so that missing attributes are
              populated from the parrent's Meta if any.
    """

    # A very rudimentary connection pool.
    _connections = {}

    def __new__(mcs, name, bases, attrs):
        new_class = super(ModelBase,
                          mcs).__new__(mcs, name, bases, attrs)
        parents = [b for b in bases if isinstance(b, ModelBase)]
        if not parents:
            # If this isn't a subclass of Model, don't do anything special.
            return new_class

        # Processing Model metadata.
        try:
            meta = getattr(new_class, 'Meta')
        except AttributeError:
            meta = None
        else:
            # Won't need the original metadata container anymore.
            delattr(new_class, 'Meta')

        schema_fields = {}
        for kattr, attr in attrs.items():
            if isinstance(attr, fields.Field):
                schema_fields[kattr] = attr
                delattr(new_class, kattr)
        meta.schema = type('schema', (ExtSchema,), schema_fields)
        options = _Options(meta)
        options.collection = options.collection or to_underscore(name)
        if not hasattr(options, 'auto_modified_datetime'):
            options.auto_modified_datetime = True

        if options.interface:
            new_class._meta = None
            new_class.database = None
            new_class.collection = DummyCollection
            return new_class

        if not (options.host and options.port and options.database):
            raise Exception(
                'Model {} improperly configured: {} {} {}'.format(
                    name, options.host, options.port, options.database))

        # Checking connection pool for an existing connection.

        # ready for replicaset
        #if isinstance(options.host, list):
        #   options.host = options.host[0]

        #hostport = options.host, options.port
        hostport = options.host
        hostport_key = '_'.join(hostport)
        if hostport_key in mcs._connections:
            connection = mcs._connections[hostport_key]
        else:
            # _connect=False option
            # creates :class:`pymongo.connection.Connection` object without
            # establishing connection. It's required if there is no running
            # mongodb at this time but we want to create :class:`Model`.
            # False option doesn't work with pymongo 2.4 using master/slave
            # cluster
            connection_args = {}
            if isinstance(options.host, list) and len(options.host) > 1:
                connection_args = {
                    'replicaset': options.replicaset,
                    'readPreference': options.readPreference,
                    'w': options.w,
                    'journal': options.journal
                }
            connection = Connection(hostport, tz_aware=True, **connection_args)
            mcs._connections[hostport_key] = connection
            if options.username and options.password:
                connection['admin'].authenticate(options.username, options.password)

        new_class._meta = options
        new_class.connection = connection
        new_class.database = connection[options.database]
        new_class.collection = options.collection_class(
            new_class.database, options.collection, document_class=new_class)

        if options.drop_index:
            new_class.collection.drop_indexes()

        if options.auto_index:
            for _ in range(3):
                if new_class.auto_index():
                    break

        new_class.auto_modified_datetime = options.auto_modified_datetime

        return new_class

    def auto_index(mcs):
        """Builds all indices, listed in model's Meta class.

           >>> class SomeModel(Model)
           ...     class Meta:
           ...         indices = (
           ...             Index('foo'),
           ...         )

        .. note:: this will result in calls to
                  :meth:`pymongo.collection.Collection.ensure_index`
                  method at import time, so import all your models up
                  front.
        """
        returns = []
        for index in mcs._meta.indices:
            try:
                returns.append(index.ensure(mcs.collection))
            except Exception as ex:
                log.exception('Minimongo model auto-index exception: %s', ex)
        return not any(returns)




class AttrDict(dict):
    def __init__(self, initial=None, from_db=False, **kwargs):
        # Make sure that during initialization, that we recursively apply
        # AttrDict.  Maybe this could be better done with the builtin
        # defaultdict?
        if initial:
            self._meta.initializing = from_db
            if hasattr(self._meta, 'schema'):
                for field_name, field in self._meta.schema._declared_fields.items():
                    if field_name not in initial:
                        if field.default != missing:
                            initial[field_name] = field.default
                        elif field.allow_none:
                            initial[field_name] = None
            for key, value in six.iteritems(initial):
                # Can't just say self[k] = v here b/c of recursion.
                self.__setitem__(key, value)
            self._meta.initializing = False
        # Process the other arguments (assume they are also default values).
        # This is the same behavior as the regular dict constructor.
        for key, value in six.iteritems(kwargs):
            self.__setitem__(key, value)
        super(AttrDict, self).__init__()


    # These lines make this object behave both like a dict (x['y']) and like
    # an object (x.y).  We have to translate from KeyError to AttributeError
    # since model.undefined raises a KeyError and model['undefined'] raises
    # a KeyError.  we don't ever want __getattr__ to raise a KeyError, so we
    # 'translate' them below:
    def __getattr__(self, attr):
        try:
            return super(AttrDict, self).__getitem__(attr)
        except KeyError as excn:
            raise AttributeError(excn)

    def __setattr__(self, attr, value):
        try:
            # Okay to set directly here, because we're not recursing.
            self[attr] = value
        except KeyError as excn:
            raise AttributeError(excn)

    def __delattr__(self, key):
        try:
            return super(AttrDict, self).__delitem__(key)
        except KeyError as excn:
            raise AttributeError(excn)

    def __setitem__(self, key, value):
        # print("AttrDict.SET", key, value)
        # Coerce all nested dict-valued fields into AttrDicts
        # new_value = value
        # if isinstance(value, dict):
        #     new_value = AttrDict(value)
        return super(AttrDict, self).__setitem__(key, value)


@six.python_2_unicode_compatible
@six.add_metaclass(ModelBase)
class Model(AttrDict):
    """Base class for all Minimongo objects.

    >>> class Foo(Model):
    ...     class Meta:
    ...         database = 'somewhere'
    ...         indices = (
    ...             Index('bar', unique=True),
    ...         )
    ...
    >>> foo = Foo(bar=42)
    >>> foo
    {'bar': 42}
    >>> foo.bar == 42
    True
    """
    def __str__(self):
        return '{}({})'.format(self.__class__.__name__,
                           super(Model, self).__str__())

    def __setitem__(self, key, value):
        # Go through the defined list of field mappers.  If the fild
        # matches, then modify the field value by calling the function in
        # the mapper.  Mapped fields must have a different type than their
        # counterpart, otherwise they'll be mapped more than once as they
        # come back in from a find() or find_one() call.
        # if self._meta and self._meta.field_map:
        #     for matcher, mogrify in self._meta.field_map:
        #         if matcher(key, value):
        #             new_value = mogrify(value)
        #             if type(new_value) == type(value):
        #                 raise Exception(
        #                     "Field mapper didn't change field type!")
        #             value = new_value
        if not self._meta.initializing and hasattr(self._meta, 'schema') and key in self._meta.schema._declared_fields:
            if self._meta.strict:
                result = self._meta.schema().load({key: value}, partial=True)
                if key in result.errors:
                    raise ValueError("%s=[%s] (%s): %s" % (key, value, type(value), result.errors[key][0]))
            field = self._meta.schema._declared_fields[key]
            try:
                if field.__class__.__name__ == 'String':
                    value = six.u(value)
                elif field.__class__.__name__ in ('Number', 'Integer'):
                    value = int(value)
                elif field.__class__.__name__ == 'Decimal':
                    value = float(value)
                elif field.__class__.__name__ == 'Boolean':
                    value = False if value in ('0', 0) else bool(value)
                elif field.__class__.__name__ == 'ObjectIdField' and value is not None:
                    value = ObjectId(value)
            except:
                pass
        super(Model, self).__setitem__(key, value)

    def __delattr__(self, key):
        if self._meta and hasattr(self._meta, 'schema') and key in self._meta.schema._declared_fields:
            field = self._meta.schema._declared_fields[key]
            if field.required:
                raise KeyError('Unable to delete required field: %s' % (key))
        super(Model, self).__delitem__(key)

    def dbref(self, with_database=True, **kwargs):
        """Returns a DBRef for the current object.

        If `with_database` is False, the resulting :class:`pymongo.dbref.DBRef`
        won't have a :attr:`database` field.

        Any other parameters will be passed to the DBRef constructor, as per
        the mongo specs.
        """
        if not hasattr(self, '_id'):
            self._id = ObjectId()

        database = self._meta.database if with_database else None
        return DBRef(self._meta.collection, self._id, database, **kwargs)

    def remove(self):
        """Remove this object from the database."""
        # return self.collection.remove(self._id)
        return self.collection.delete_one({ "_id": self._id })

    def mongo_update(self, values=None, **kwargs):
        """Update database data with object data."""
        # Allow to update external values as well as the model itself
        if not values:
            # Remove the _id and wrap self into a $set statement.
            self_copy = copy.copy(self)
            del self_copy._id
            values = {'$set': self_copy}
        self.collection.update({'_id': self._id}, values, **kwargs)
        return self

    def save(self, *args, **kwargs):
        """Save this object to it's mongo collection."""
        if hasattr(self._meta, 'schema'):
            for field_name, field in self._meta.schema._declared_fields.items():
                if field_name not in self and field.required:
                    raise KeyError('Missing field: %s' % (field_name))
            if self._meta.strict:
                result = self._meta.schema().load(self)
                for key, error in result.errors.items():
                    raise ValueError("%s=[%s] (%s): %s" % (key, self[key], type(self[key]), error[0]))
                unsets = []
                for key, value in self.items():
                    if key not in self._meta.schema._declared_fields and key not in ['_id']:
                        unsets.append(key)
                for key_to_unset in unsets:
                    del(self[key_to_unset])
        if self._meta.auto_modified_datetime:
            self['modified_datetime'] = datetime.datetime.utcnow()
        try:
            if '_id' not in self:
                result = self.collection.insert_one(self)
                self._id = result.inserted_id
            else:
                self.collection.replace_one({'_id': self._id}, self, upsert=True, *args, **kwargs)
        except DuplicateKeyError as ex:
            raise ValueError(ex.details.get('errmsg'))
        return self

    def load(self, fields=None, **kwargs):
        """Allow partial loading of a document.
        :attr:fields is a dictionary as per the pymongo specs

        self.collection.find_one( self._id, fields={'name': 1} )

        """
        values = self.collection.find_one({'_id': self._id},
                                          fields=fields, **kwargs)
        # Merge the loaded values with whatever is currently in self.
        self.update(values)
        return self

    def id(self):
        return self._id

    @classmethod
    def getSchemaWithFields(cls, schema_id, list_of_fields, additional_fields={}, with_id=True):
        if hasattr(cls._meta, 'schema'):
            schema_fields = {field: cls._meta.schema._declared_fields[field] for field in list_of_fields if field in cls._meta.schema._declared_fields}
            if with_id:
                schema_fields['_id'] = fields.ObjectId()
            schema_fields.update(additional_fields)
            return type(schema_id, (ExtSchema,), schema_fields)
        return None

# Utils.

def to_underscore(string):
    """Converts a given string from CamelCase to under_score.

    >>> to_underscore('FooBar')
    'foo_bar'
    """
    new_string = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', string)
    new_string = re.sub(r'([a-z\d])([A-Z])', r'\1_\2', new_string)
    return new_string.lower()
