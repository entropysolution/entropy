from flask import request
from bson.errors import InvalidId
from bson.objectid import ObjectId
from common.jsonify import jsonify
from werkzeug.routing import BaseConverter, ValidationError

class ObjectIDConverter(BaseConverter):
    def to_python(self, value):
        try:
            return ObjectId(value)
        except (InvalidId, ValueError, TypeError):
            raise ValidationError()
    def to_url(self, value):
        return str(value)

def jquery_datatable(mongo_tbl, source_columns, search_filter, cols_to_str_convert=None, required_filter=None, return_as_json=True, fixed_column_sorting=[], override_column_sort=[], cols_to_int_convert=None):
    #-- SAMPLE USAGE:
    # source_columns = [
    #   'name',
    # ]
    # search_filter = []
    # if request.form.get('txt_search_val') != '':
    #   search_filter.append({'name': {'$regex': request.form.get('search_val'), '$options': '-i'}})
    # return jquery_datatable(app.db.categories, source_columns, search_filter)
    # ------------------------------------------------------------------------------------------------

    # @cols_to_str_convert (list)   --> list of columns to be converted to string
    # @cols_to_int_convert (list)   --> list of columns to be converted to int
    # @required_filter (dict)       --> dict of columns to filter
    # @fixed_column_sorting (list)  --> prioritizes this column to be sorted followed by the regular sort clicked from the table's header column
    #   - example: fixed_column_sorting = ['timestamp', -1]

    # rec_draw = int(request.form.get('draw'))
    rec_sort_column = int(request.form.get('order[0][column]'))
    rec_sort_order = str(request.form.get('order[0][dir]'))
    # rec_search_val = str(request.form.get('search[value]'))
    rec_start = int(request.form.get('start'))
    if request.form.get('sel_pagination_count_val'):
        rec_limit = int(request.form.get('sel_pagination_count_val', 10))
    else:
        rec_limit = int(request.form.get('length', 10))

    record_search_filter = {}
    if required_filter is not None:
        record_search_filter = required_filter

    if len(search_filter) > 0:
        record_search_filter['$or'] = search_filter

    cols_to_display = {}
    for col in source_columns:
        cols_to_display[col] = True

    #-- apply priority sort if needed
    sort = 1 if rec_sort_order == 'asc' else -1
    if len(override_column_sort) > 0:
        tbl_sort = [tuple(override_column_sort)]
    elif len(fixed_column_sorting) > 0:
        tbl_sort = [tuple(fixed_column_sorting), (source_columns[rec_sort_column], sort)]
    else:
        tbl_sort = [(source_columns[rec_sort_column], sort)]

    records_total_cnt = mongo_tbl.find(record_search_filter, {'_id': True}).count()
    records = list(mongo_tbl.find(record_search_filter, cols_to_display).sort(tbl_sort).limit(rec_limit).skip(rec_start))

    for rec in records:
        rec['_id'] = str(rec['_id'])
        #- convert ObjectId types into string, so it will not cause an error when called by jsonify
        if cols_to_str_convert is not None:
            for col in cols_to_str_convert:
                rec[col] = str(rec[col])
        if cols_to_int_convert is not None:
            for col in cols_to_int_convert:
                rec[col] = int(rec.get(col,0))
        #- force place a column name if not exists from the record
        for col in source_columns:
            if col not in rec:
                rec[col] = ''

    records_datatable = {
        'recordsTotal': records_total_cnt,
        'recordsFiltered': records_total_cnt,
        'data': records
    }
    if return_as_json:
        return jsonify(records_datatable)
    else:
        return records_datatable