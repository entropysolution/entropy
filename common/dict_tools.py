import _pickle as pickle
from collections import Mapping

def deepcopy(d):
	return pickle.loads(pickle.dumps(d, -1))

def merge_dicts(base_dict, append_dict, overwrite=False):
	"""
    Recursively merges append_dict into base_dict
    overwrite True will merge in-place
    """
	if not isinstance(base_dict, dict) or not isinstance(append_dict, dict):
		return None
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
