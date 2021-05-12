def number_format(input_val, decimal_digits=0):
    format_str = '{0:,.%sf}' % decimal_digits
    return format_str.format(float(input_val))
