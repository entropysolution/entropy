from datetime import datetime, timedelta
from uuid import uuid4
from flask.sessions import SessionInterface, SessionMixin
from werkzeug.datastructures import CallbackDict
from pymongo import MongoClient


class MongoSession(CallbackDict, SessionMixin):
	def __init__(self, initial=None, sid=None, store=None):
		CallbackDict.__init__(self, initial)
		self.sid = sid
		self.modified = False
		self.store = store

	def clear(self):
		self.store.remove({'sid': self.sid})
		super(MongoSession, self).clear()

	def count(self, username=None):
		filter = {'data.user': {'$exists': True}}
		if username is not None:
			filter['data.user.username'] = username
		return self.store.find(filter).count()


class MongoSessionInterface(SessionInterface):
	def __init__(self, config={}, app=None):
		if config == {}:
			raise Exception('MongoSessionInterface misconfiguration')

		expireAfterSeconds = 3600
		client = MongoClient(config['host'], 27017)
		self.store = client[config['database']][config['collection']]

		if app is not None:
			expireAfterSeconds = app.permanent_session_lifetime.total_seconds()

		self.store.drop_indexes()
		self.store.ensure_index('sid')
		self.store.ensure_index('modified', expireAfterSeconds=expireAfterSeconds)

	def open_session(self, app, request):
		sid = request.cookies.get(app.session_cookie_name)
		if sid:
			stored_session = self.store.find_one({'sid': sid})
			if stored_session:
				if stored_session.get('expiration') > datetime.utcnow():
					return MongoSession(initial=stored_session['data'],
										sid=stored_session['sid'], store=self.store)
		sid = str(uuid4())
		return MongoSession(sid=sid, store=self.store)

	def save_session(self, app, session, response):
		domain = self.get_cookie_domain(app)
		if not session:
			response.delete_cookie(app.session_cookie_name, domain=domain)
			return
		if self.get_expiration_time(app, session):
			expiration = self.get_expiration_time(app, session)
		else:
			expiration = datetime.utcnow() + timedelta(hours=1)
		self.store.update({'sid': session.sid},
						  {'sid': session.sid,
						   'data': session,
						   'modified': datetime.utcnow(),
						   'expiration': expiration}, True)
		response.set_cookie(app.session_cookie_name, session.sid,
							expires=self.get_expiration_time(app, session),
							httponly=True, domain=domain)
