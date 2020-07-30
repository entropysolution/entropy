import string
import random
from copy import deepcopy
from unittest import TestCase
from collections import Mapping
from bson.objectid import ObjectId
from micromongo import Model, Index, fields, validate

def genid():
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(9))

def merge_recursion(d1, d2):
	for k, v2 in d2.items():
		v1 = d1.get(k)
		if (isinstance(v1, Mapping) and isinstance(v2, Mapping)):
			merge_recursion(v1, v2)
		else:
			d1[k] = v2

def merge_dicts(base_dict, append_dict, overwrite=False):
	if not overwrite:
		copy_dict = deepcopy(base_dict)
		merge_recursion(copy_dict, append_dict)
		return copy_dict
	if overwrite:
		merge_recursion(base_dict, append_dict)
		return base_dict

class StrictUser(Model):
    username = fields.Str(required=True, validate=validate.Length(min=3))
    password = fields.Str(required=True)
    access_count = fields.Number(default=0)
    gender = fields.Str(validate=validate.OneOf(choices=['M', 'F']))
    profile = fields.Dict(default={})
    active = fields.Boolean(default=True)
    parent_user_id = fields.ObjectId(default=None, allow_none=True)
    profile_set_id = fields.ObjectId(required=True)
    
    class Meta:
        host = 'localhost'
        database = 'micromongo_test'
        collection = "users"        
        indices = (
            Index('username', unique=True),
        )
        strict = True
    @staticmethod
    def getUserFromUsername(username):
        return User.collection.find_one({'username': username})

    def update(self, args):
        merge_dicts(self, args, True)


class LenientUser(Model):
    username = fields.Str(required=True, validate=validate.Length(min=3))
    password = fields.Str(required=True)
    access_count = fields.Number(default=0)
    gender = fields.Str(validate=validate.OneOf(choices=['M', 'F']))
    profile = fields.Dict(default={})
    active = fields.Boolean(default=True)
    parent_user_id = fields.ObjectId(default=None, allow_none=True)
    profile_set_id = fields.ObjectId(required=True)
    
    class Meta:
        host = 'localhost'
        database = 'micromongo_test'
        collection = "users"        
        indices = (
            Index('username', unique=True),
        )
        strict = False
    @staticmethod
    def getUserFromUsername(username):
        return User.collection.find_one({'username': username})

    def update(self, args):
        merge_dicts(self, args, True)



class TestModel(TestCase):
    def test_strict_create(self):
        username = genid()
        u = StrictUser({"username": username, "password": "pw", "profile_set_id": ObjectId(), "y": 2, "gender": "M"})
        self.assertTrue(u['username'] == username)
        self.assertTrue(u['password'] == 'pw')
        self.assertTrue(u['profile'] == {})
        self.assertTrue(u['access_count'] == 0)
        self.assertTrue(u['parent_user_id'] == None)
        self.assertTrue(u['active'] == True)
        u = u.save()
        self.assertTrue('y' not in u)

    def test_lenient_create(self):
        username = genid()
        u = LenientUser({"username": username, "password": "pw", "profile_set_id": ObjectId(), "y": 2, "gender": "M"})
        self.assertTrue(u['username'] == username)
        self.assertTrue(u['password'] == 'pw')
        self.assertTrue(u['profile'] == {})
        self.assertTrue(u['access_count'] == 0)
        self.assertTrue(u['parent_user_id'] == None)
        self.assertTrue(u['active'] == True)
        u = u.save()
        self.assertTrue('y' in u)

    def test_create_exception(self):
        with self.assertRaises(ValueError):
            u = StrictUser({"username": "u", "password": "pw", "profile_set_id": ObjectId(), "y": 2})
        with self.assertRaises(ValueError):
            StrictUser({"username": "user01", "password": True, "profile_set_id": ObjectId()})
        with self.assertRaises(KeyError):
            StrictUser({"username": "user01", "profile_set_id": ObjectId()}).save()
        with self.assertRaises(ValueError):
            StrictUser({"username": "user01", "password": True}).save()
        with self.assertRaises(ValueError):
            StrictUser({"username": "user01", "password": "pw", "profile": "=", "profile_set_id": ObjectId()})
        with self.assertRaises(ValueError):
            StrictUser({"username": "user01", "password": "pw", "profile_set_id": ObjectId(), "active": None})
        with self.assertRaises(ValueError):
            StrictUser({"username": "user01", "password": "pw", "profile_set_id": ObjectId(), "access_count": "X"})
        with self.assertRaises(ValueError):
            StrictUser({"username": "user01", "password": "pw", "profile_set_id": ObjectId(), "parent_user_id": "11241241241"})
        with self.assertRaises(ValueError):
            StrictUser({"username": "user01", "password": "pw", "profile_set_id": ObjectId(), "gender": "X"})

    def test_strict_setattr_exceptions(self):
        u = StrictUser({"username": "user01", "password": "pw", "profile_set_id": ObjectId(), "parent_user_id": ObjectId()})
        with self.assertRaises(ValueError):
            u.username = 1
        with self.assertRaises(ValueError):
            u.access_count = "X"
        with self.assertRaises(ValueError):
            u.active = "X"
        with self.assertRaises(ValueError):
            u.profile_set_id = None
        u.parent_user_id = None # should be ok
        with self.assertRaises(KeyError):
            del(u.username)

    def test_lenient_setattr_exceptions(self):
        username = genid()
        u = LenientUser({"username": username, "password": "pw", "profile_set_id": ObjectId(), "parent_user_id": ObjectId()})
        u.username = 1
        u.access_count = "X"
        u.active = "X"
        u.profile_set_id = None
        u.parent_user_id = None # should be ok
        with self.assertRaises(KeyError):
            del(u.username)
        u.save()

    def test_update_exceptions(self):
        u = StrictUser({"username": "user01", "password": "pw", "profile_set_id": ObjectId(), "parent_user_id": ObjectId()})
        with self.assertRaises(ValueError):
            u.update({'username': 'X'})
        with self.assertRaises(ValueError):
            u.update({'username': 1})

    def test_get_fields_schema_with_id(self):
        s = StrictUser.getSchemaWithFields('schema', ['username', 'password'])._declared_fields
        self.assertEqual(len(s), 3)
        self.assertTrue('username' in s)
        self.assertTrue('password' in s)
        self.assertTrue('_id' in s)

    def test_get_fields_schema_without_id(self):
        s = StrictUser.getSchemaWithFields('schema', ['username', 'password'], with_id=False)._declared_fields
        self.assertEqual(len(s), 2)
        self.assertTrue('username' in s)
        self.assertTrue('password' in s)

