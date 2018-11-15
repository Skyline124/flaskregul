import sys

sys.path.insert(0,"/var/www/flaskregul")
sys.path.insert(0,"/var/www/flaskregul/backend")
sys.path.insert(0,"/home/pi/.local/lib/python3.5/site-packages")

from __init__ import app as application
from __init__ import *

print("Starting... // temperature = " + str(status["temperature"]))
# Motor checking for initPosition
print("Motor intialization...")
motor.initPosition()

