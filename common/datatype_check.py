from bson import ObjectId

def isfloat(x):
   try:
       a = float(x)
   except ValueError:
       return False
   else:
       return True

def isint(x):
   try:
       a = float(x)
       b = int(a)
   except ValueError:
       return False
   else:
       return a == b

def isobjectid(x):
   try:
       a = ObjectId(x)
   except:
       return False
   else:
       return True
