from calendar import timegm
from itertools import tee, zip_longest
from pytz import timezone as ptimezone
from datetime import datetime, timezone, timedelta

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
    # return datetime.utcnow().replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc)

def tolocaltime(dt, tz_region):
    tz = ptimezone(tz_region)
    return dt.astimezone(tz)

def convert_sec_to_str(seconds):
    negative = False
    if seconds < 0:
        negative = True
        seconds = abs(seconds)
    td = timedelta(seconds=seconds)
    def plural(n):
        if n>1: return 's'
        return ''
    if td == timedelta(0):
        return '0 seconds'
    out = []
    y, d = divmod(td.days, 365)
    if y: out.append('%d year' % y + plural(y))
    m, d = divmod(d, 30)
    if m: out.append('%d month' % m + plural(m))
    if d: out.append('%d day' % d + plural(d))
    h, s = divmod(td.seconds, 60*60)
    if h: out.append('%d hour' % h + plural(h))
    m, s = divmod(s, 60)
    if m: out.append('%d minute' % m + plural(m))
    if s: out.append('%d second' % s + plural(s))
    if negative:
        out.append('ago')
    return ' '.join(out)
