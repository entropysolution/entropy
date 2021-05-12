from time import mktime
from calendar import timegm
from itertools import tee, zip_longest
from pytz import timezone as ptimezone, utc
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

def last_day_of_month(dt):
    next_month = dt.replace(day=28, hour=23, minute=59, second=59) + timedelta(days=4)  # this will never fail
    return next_month - timedelta(days=next_month.day)

def convert_str_to_date(input_val, date_format='%m/%d/%Y %H:%M', tz=utc):
    try:
        input_val = datetime.strptime(input_val, date_format)
        tz_offset = tz.utcoffset(input_val)
        input_val = input_val - tz_offset
        input_val = input_val.replace(tzinfo=utc)
    except:
        return None
    return input_val

def convert_date_to_str(input_val, date_format='%Y-%m-%d %H:%M:%S', tz=utc):
    try:
        input_val = input_val.astimezone(tz).strftime(date_format)
    except:
        return ''
    return input_val

def convert_str_to_date2(input_val):
    try:
        input_val = datetime.datetime.strptime(input_val, '%m/%d/%Y')
    except:
        return None
    return input_val

def utc_mktime(utc_tuple):
    """Returns number of seconds elapsed since epoch
    Note that no timezone are taken into consideration.
    utc tuple must be: (year, month, day, hour, minute, second)
    """
    if len(utc_tuple) == 6:
        utc_tuple += (0, 0, 0)
    return mktime(utc_tuple) - mktime((1970, 1, 1, 0, 0, 0, 0, 0, 0))

def datetime_to_timestamp(dt):
    """Converts a datetime object to UTC timestamp"""
    return int(utc_mktime(dt.timetuple())) * 1000
