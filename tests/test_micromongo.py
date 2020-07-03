from copy import deepcopy
from unittest import TestCase
from collections import Mapping
from bson.objectid import ObjectId
from micromongo import Model, Index, fields, validate

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

class User(Model):
    username = fields.Str(required=True, validate=validate.Length(min=3))
    password = fields.Str(required=True)
    access_count = fields.Number(default=0)
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

    @staticmethod
    def getUserFromUsername(username):
        return User.collection.find_one({'username': username})

    def update(self, args):
        merge_dicts(self, args, True)


class TestModel(TestCase):
    def test_create(self):
        u = User({"username": "user01", "password": "pw", "profile_set_id": ObjectId(), "y": 2})
        self.assertTrue(u['username'] == 'user01')
        self.assertTrue(u['password'] == 'pw')
        self.assertTrue(u['profile'] == {})
        self.assertTrue(u['access_count'] == 0)
        self.assertTrue(u['parent_user_id'] == None)
        self.assertTrue(u['active'] == True)
    
    def test_create_exception(self):
        with self.assertRaises(ValueError):
            u = User({"username": "u", "password": "pw", "profile_set_id": ObjectId(), "y": 2})
        with self.assertRaises(ValueError):
            User({"username": "user01", "password": True, "profile_set_id": ObjectId()})
        with self.assertRaises(KeyError):
            User({"username": "user01", "profile_set_id": ObjectId()})
        with self.assertRaises(KeyError):
            User({"username": "user01", "password": True})
        with self.assertRaises(ValueError):
            User({"username": "user01", "password": "pw", "profile": "=", "profile_set_id": ObjectId()})
        with self.assertRaises(ValueError):
            User({"username": "user01", "password": "pw", "profile_set_id": ObjectId(), "active": None})
        with self.assertRaises(ValueError):
            User({"username": "user01", "password": "pw", "profile_set_id": ObjectId(), "access_count": "X"})
        with self.assertRaises(ValueError):
            User({"username": "user01", "password": "pw", "profile_set_id": ObjectId(), "parent_user_id": "11241241241"})

    def test_setattr_exceptions(self):
        u = User({"username": "user01", "password": "pw", "profile_set_id": ObjectId(), "parent_user_id": ObjectId()})
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

    def test_update_exceptions(self):
        u = User({"username": "user01", "password": "pw", "profile_set_id": ObjectId(), "parent_user_id": ObjectId()})
        with self.assertRaises(ValueError):
            u.update({'username': 'X'})
        with self.assertRaises(ValueError):
            u.update({'username': 1})