from micromongo import Model, Index, fields
from bson.objectid import ObjectId

class User(Model):
    username = fields.Str()
    password = fields.Str()
    access_count = fields.Number(default=0)
    profile = fields.Dict(default={})
    active = fields.Boolean(default=True)
    parent_user_id = fields.ObjectId(default=None, allow_none=True)

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

foo = User({"username": "user01", "password": "pw", "y": 2})
#foo.password = "asdf"
foo.count = 1
# print foo
# print foo.username
# print foo.password
# print foo._meta.schema._declared_fields
foo.save()
print foo

user = User.getUserFromUsername('user01')
user.active = 'X'