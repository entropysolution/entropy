ACL_INHERITED = 0
ACL_NO_ACCESS = 1
ACL_VIEW = 2
ACL_MODIFY = 3
ACL_ADD_DELETE = 4

def get_admin_acl():
	output = {}
	for key, val in auth_objects.items():
		output[key] = 4 #- ACL_ADD_DELETE
	return output

def get_user_acl(user_privileges_dict):
	output = {}
	acl_obj = ACL(auth_objects, user_privileges_dict)
	for key, val in auth_objects.items():
		output[key] = acl_obj.allowedPrivilege(key)
	return output

def get_public_acl():
	return {key: 2 if key in ['map'] else 1 for key, value in auth_objects.items()}

def page_has_no_access(user_privileges, current_page):
	if current_page in auth_objects:
		return user_privileges[current_page] < 2  #ACL_VIEW = 2
	else:
		return True

class ACL:
	auth_objects = {}
	objects = {}
	objects_2d = []
	children = {}
	depth = -1
	admin = False
	root = False

	def __init__(self, auth_objects, user_privileges, admin=False):
		self.objects_2d = []
		self.admin = admin
		# print 'ACL init', user_privileges
		self.auth_objects = auth_objects
		for auth_object_id in auth_objects:
			auth_object = auth_objects[auth_object_id]
			# print auth_object_id
			# print auth_object

			if auth_object_id in user_privileges:
				auth_object['privilege'] = int(user_privileges[auth_object_id])
			else:
				auth_object['privilege'] = auth_object['default']

			if auth_object['parent_id'] not in self.children:
				self.children[auth_object['parent_id']] = {}
			self.children[auth_object['parent_id']][auth_object_id] = auth_object

			if auth_object['parent_id'] == None:
				self.objects[auth_object_id] = auth_object

		self.objects = self.loadChildren(self.objects)

	def loadChildren(self, objects):
		#print 'LOADCHILDREN', objects
		self.depth += 1
		for obj_id in objects:
			obj = objects[obj_id]
			self.objects_2d.append({
				'id': obj_id,
				'name': '%s%s' % ('&nbsp;&nbsp;&nbsp;&nbsp;' * self.depth, obj['name']),
				'possible_privileges': obj['possible_privileges'],
				'privilege': obj['privilege']
			})
			if obj_id in self.children:
				obj['children'] = self.children[obj_id]
				obj['children'] = self.loadChildren(obj['children'])
		self.depth -= 1
		return objects

	def isAuthorized(self, obj_id, privilege):
		if self.admin:
			return True
		if self.auth_objects[obj_id]['privilege'] != ACL_INHERITED:
			return self.auth_objects[obj_id]['privilege'] >= privilege
		else:
			if self.auth_objects[obj_id]['parent_id'] != None:
				return self.isAuthorized(self.auth_objects[obj_id]['parent_id'], privilege)
			else:
				return False

	def allowedPrivilege(self, obj_id):
		if self.admin:
			return ACL_ADD_DELETE

		if self.auth_objects[obj_id]['privilege'] != ACL_INHERITED:
			return self.auth_objects[obj_id]['privilege']
		else:
			if self.auth_objects[obj_id]['parent_id'] != None:
				return self.allowedPrivilege(self.auth_objects[obj_id]['parent_id'])
			else:
				return False

	def setDefaultPrivilege(self, obj_id):
		if self.admin:
			return ACL_ADD_DELETE

		return self.auth_objects[obj_id]['privilege']
