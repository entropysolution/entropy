# from copy import deepcopy
# import _pickle as pickle
import ujson
from collections import Mapping
from common.jsonify import jsonify


def deepcopy(d):
	#return pickle.loads(pickle.dumps(d, -1))
	return ujson.loads(ujson.dumps(d))

def merge_dicts(base_dict, append_dict, overwrite=False):
	"""
    Recursively merges append_dict into base_dict
    overwrite True will merge in-place
    """
	if not isinstance(base_dict, dict) or not isinstance(append_dict, dict):
		return jsonify({'success': False})
	if not overwrite:
		copy_dict = deepcopy(base_dict)
		merge_recursion(copy_dict, append_dict)
		return copy_dict
	if overwrite:
		merge_recursion(base_dict, append_dict)
		return base_dict


def merge_recursion(d1, d2):
	"""Takes two dicts as arguments. Returns merged dicts by combining deeper levels recursively"""
	for k, v2 in d2.items():
		v1 = d1.get(k)
		if (isinstance(v1, Mapping) and isinstance(v2, Mapping)):
			merge_recursion(v1, v2)
		else:
			d1[k] = v2

def merge_in_place(d1, d2):
    """
    Modifies d1 in-place to contain values from d2.  If any value
    in d1 is a dictionary (or dict-like), *and* the corresponding
    value in d2 is also a dictionary, then merge them in-place.
    """
    for k,v2 in d2.items():
        v1 = d1.get(k) # returns None if v1 has no value for this key
        if ( isinstance(v1, Mapping) and
             isinstance(v2, Mapping) ):
            merge_in_place(v1, v2)
        else:
            d1[k] = v2

class SafeDict(dict):
    def __missing__(self, key):
        return ''
