from functools import wraps
from unicodedata import normalize
from .generators import generate_alphanum
from werkzeug.datastructures import ImmutableMultiDict, MultiDict


def route(bp, *args, **kwargs):
	def wrapper(f):
		@bp.route(*args, **kwargs)
		@wraps(f)
		def wrapped(*args, **kwargs):
			return f(*args, **kwargs)
		return wrapped
	return wrapper


def generate_csrf(csrf_container, *args, **kwargs):
	def wrapper(f):
		@wraps(f)
		def wrapped(*args, **kwargs):
			csrf_container['csrf_key'] = generate_alphanum(8)
			csrf_container['csrf_token'] = generate_alphanum(16)

			return f(*args, **kwargs)
		return wrapped
	return wrapper


def validate_csrf(csrf_container, request_object, abort_object, *args, **kwargs):
	def wrapper(f):
		@wraps(f)
		def wrapped(*args, **kwargs):
			if csrf_container.get('csrf_key', 'none_existing') not in request_object.form.keys():
				print('CSRF Error')
				return abort_object(412)
			csrf_container['csrf_key'] = generate_alphanum(8)
			csrf_container['csrf_token'] = generate_alphanum(16)
			return f(*args, **kwargs)
		return wrapped
	return wrapper


def validate_form(request_object, abort_object, **fields):
	def wrapper(f):
		@wraps(f)
		def wrapped(*args, **kwargs):
			for field_name, field_type in fields.items():
				field_value = request_object.form.get(field_name)
				if field_value is None and field_type is not bool:
					print('Field "%s" missing.' % (field_name))
					return abort_object(412)

				if isinstance(request_object.form, ImmutableMultiDict):
					request_object.form = MultiDict(request_object.form)

				try:
					if field_type is bool:
						request_object.form[field_name] = False if field_value in (None, '0', 'false') else True
					elif field_type is str:
						field_value = request_object.form[field_name]
						field_value = field_type(field_value).strip()
						field_value = normalize('NFKD', field_value)
						request_object.form[field_name] = field_value
					else:
						request_object.form[field_name] = field_type(field_value)
				except Exception as ex:
					print('[VF] Invalid Value "%s" for field %s (%s)' % (field_value, field_name, field_type))
					print('exception', ex)
					return abort_object(412)

				if field_type is str and len(request_object.form[field_name]) == 0:
					print('[VF] Empty value for field "%s"' % (field_name))
					return abort_object(412)

			return f(*args, **kwargs)
		return wrapped
	return wrapper
