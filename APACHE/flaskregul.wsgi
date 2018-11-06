#!/usr/bin/python
import sys
print("before insert to path")
sys.path.insert(0,"/var/www/flaskregul")
print("after insert to path")
print("before import app")
from __init__ import app as application
print("after import app")
