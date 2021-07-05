def normalize(value):
    result = ''
    if isinstance(value, str):
        for i, c in enumerate(value):
            if not c.isalnum():
                result += ' '
                continue
            result += c
    else:
        return value
    return result

from bson import ObjectId
from json import dumps
from datetime import datetime

# Used to cast ObjectId field into str
def tostrjson(record):
    if isinstance(record, dict):
        parse_dict(record)
    elif isinstance(record, list):
        for item in record:
            parse_dict(item)
    return dumps(record)


def parse_dict(record):
    for k, v in record.items():
        if (isinstance(v, ObjectId) or isinstance(v, datetime)):
            record[k] = str(v)
        elif isinstance(v, list):
            record[k] = list(map(str, v))
