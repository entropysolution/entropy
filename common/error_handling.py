import sys

def get_current_method():
    return sys._getframe(1).f_code.co_name