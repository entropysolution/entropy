def base10ToBase26Letter(num):
    ''' Converts any positive integer to Base26(letters only) with no 0th
    case. Useful for applications such as spreadsheet columns to determine which
    Letterset goes with a positive integer.
    '''
    if num <= 0:
        return ""
    elif num <= 26:
        return chr(96+num)
    else:
        return base10ToBase26Letter(int((num-1)/26))+chr(97+(num-1)%26)
