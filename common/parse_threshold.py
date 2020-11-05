import re
from common.datatype_check import isfloat, isint

def cast_field(val, field):
    cast_value = None
    if field in ['value']:
        if isint(val):
            cast_value = int(val)
        elif isfloat(val):
            cast_value = float(val)
    elif field in ['color'] and bool(re.match("#[A-Za-z0-9]{6}", val)):
        cast_value = val
    elif field in ['message'] and bool(re.match("^[ A-Za-z0-9\.\,_-]*$", val)):
        cast_value = val

    if cast_value:
        return cast_value
    else:
        raise ValueError('%s parameter is invalid' % field.title())

def threshold_save(args, record):
    field_parent1 = args.get('field_parent1')
    field_parent2 = args.get('field_parent2')
    field = args.get('field')
    value = args.get('value')

    if field_parent2 == 'normal_level': # special case
        if 'normal_levels' not in record:
            record['normal_levels'] = {}
        if field_parent1 not in record['normal_levels']:
            record['normal_levels'][field_parent1] = {}
        record['normal_levels'][field_parent1][field] = cast_field(value, field)
    else:
        if 'thresholds' not in record:
            record['thresholds'] = {}
        if field_parent1 not in record['thresholds']:
            record['thresholds'][field_parent1] = {}
        if field_parent2 not in record['thresholds'][field_parent1]:
            record['thresholds'][field_parent1][field_parent2] = {}
        record['thresholds'][field_parent1][field_parent2][field] = cast_field(value, field)
    record.save()
