def clamp(val, minimum=0, maximum=255):
    if val < minimum:
        return minimum
    if val > maximum:
        return maximum
    return val

def colorscale(hexstr, scalefactor):
    """
    Scales a hex string by ``scalefactor``. Returns scaled hex string.

    To darken the color, use a float value between 0 and 1.
    To brighten the color, use a float value greater than 1.

    >>> colorscale("#DF3C3C", .5)
    #6F1E1E
    >>> colorscale("#52D24F", 1.6)
    #83FF7E
    >>> colorscale("#4F75D2", 1)
    #4F75D2
    """
    hexstr = hexstr.strip('#')
    if scalefactor < 0 or len(hexstr) != 6:
        return hexstr
    r, g, b = int(hexstr[:2], 16), int(hexstr[2:4], 16), int(hexstr[4:], 16)
    r = clamp(r * scalefactor)
    g = clamp(g * scalefactor)
    b = clamp(b * scalefactor)
    return "#%02x%02x%02x" % (r, g, b)
    
def complementaryColor(color):
    # strip the # from the beginning
    color = color.strip('#')
    # convert the string into hex
    color = int(color, 16)
    # invert the three bytes
    # as good as substracting each of RGB component by 255(FF)
    comp_color = 0xFFFFFF ^ color
    # convert the color back to hex by prefixing a #
    comp_color = "#%06X" % comp_color
    # return the result
    return comp_color
    
def hex_to_rgb(hex):
     hex = hex.lstrip('#')
     hlen = len(hex)
     return tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))
