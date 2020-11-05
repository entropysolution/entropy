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
