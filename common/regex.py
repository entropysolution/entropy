import re

mac_re = re.compile('^([0-9A-Fa-f]{2}){5}([0-9A-Fa-f]{2})$')
domain_re = re.compile('^(?=.{4,255}$)([a-zA-Z0-9][a-zA-Z0-9-]{,61}[a-zA-Z0-9]\.)+[a-zA-Z0-9]{2,5}$')