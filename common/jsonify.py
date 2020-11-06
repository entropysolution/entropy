import ujson
import common.fixed_datetime as datetime
from bson import ObjectId
from werkzeug import Response
try:
	import simplejson as json
except ImportError:
	try:
		import json
	except ImportError:
		raise ImportError

class MongoJsonEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, (datetime.datetime, datetime.date)):
			return obj.isoformat()
		elif isinstance(obj, ObjectId) or isinstance(obj, str) or isinstance(obj, type):
			return str(obj)
		return json.JSONEncoder.default(self, obj)

def jsonify(*args, **kwargs):
	return Response(json.dumps(dict(*args, **kwargs), cls=MongoJsonEncoder), mimetype='application/json')

def json_encode(*args, **kwargs):
	return json.dumps(dict(*args, **kwargs), cls=MongoJsonEncoder)

def json_decode(s):
	return ujson.loads(s)

def jsonify_with_headers(args, headers={}):
	return Response(json.dumps(args, cls=MongoJsonEncoder), mimetype='application/json', headers=headers)

def fast_json_encode(*args, **kwargs):
	return ujson.dumps(dict(*args, **kwargs))
