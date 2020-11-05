from calendar import timegm
from itertools import tee, zip_longest
from datetime import datetime, timezone

def pairwise(iterable):
    a, b = tee(iterable)
    next(b, None)
    return zip_longest(a, b, fillvalue=None)

def group(sorted_iterable, delta):
    pairs = pairwise(sorted_iterable)
    for start, tmp in pairs:
        if not (isinstance(start, datetime) and isinstance(tmp, datetime)):
            continue
        if tmp - start <= delta:
            for end, tmp in pairs:
               if tmp is None or not (tmp - end <= delta):
                   break
            yield start, end
        else:
            yield start, 

def utcepoch():
    return timegm(datetime.utcnow().utctimetuple())

def utcnow():
    return datetime.now(timezone.utc)