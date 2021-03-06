from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy


# Time zones
import pytz
# time & atexit: scheduler of temperature recording
import time
import atexit
from apscheduler.schedulers.background import BackgroundScheduler

import datetime
import math
import requests
import random as rdm
from backend import motor as motor
import board
import busio
import adafruit_sht31d

i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_sht31d.SHT31D(i2c)

tz = pytz.timezone('Europe/Paris')

status = {
    'temperature': sensor.temperature,
    'humidity': sensor.relative_humidity,
    'regulation': 'manual',
    'percentageMotor': 0,
    'motorStatus': "OK"
}

# ## ------------------------ ## #
# ## --       SERVER       -- ## #
# ## ------------------------ ## #
FLASK_DEBUG = 1
app = Flask(__name__,
            static_folder="./dist/static",
            template_folder="./dist")

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////var/www/flaskregul/test1.db'
db = SQLAlchemy(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


# ##           RANDOM TEST         ## #
@app.route('/api/random')
def random_number():
    response = {
        'randomNumber': rdm.randint(1, 100)
    }
    return jsonify(response)


# ##   INITITALIZATION OF MOTOR POSITION    ## #
@app.route('/api/initmotor')
def init_motor_request():
    global status

    print("Motor asked for init... ")
    isOK = motor.initPosition()
    status["motorStatus"] = isOK
    status["percentageMotor"] = 0
    if isOK == "OK":
        return jsonify({'motorStatus': isOK})
    else:
        return jsonify({'motorStatus': isOK}), 500


# ##           GET TEMPERATURE         ## #
@app.route('/api/gettemperature', methods=['GET'])
def send_temperature():
    # demand = float(request.get_data('demanded'))
    temp = measure_temperature()
    return jsonify({'temperature': temp})


# ##           GET HUMIDITY         ## #
@app.route('/api/gethumidity', methods=['GET'])
def send_humidity():
    # demand = float(request.get_data('demanded'))

    return jsonify({'humidity': measure_humidity()})


# ##           GET TEMPERATURE HISTORY         ## #
def date_handler(obj):
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    else:
        return None


@app.route('/api/gettemperaturehistory', methods=['GET'])
def send_temperature_history():
    db.create_all()  # only to be created once
    # demand = float(request.get_data('demanded'))
    Temp_History = get_measurement_history()
    Dictionary = {'time': [], 'temperature': []}
    for i in range(1, Temp_History.__len__()):
        Dictionary['time'].append(Temp_History[i].time)
        Dictionary['temperature'].append(Temp_History[i].temperature)

    return jsonify(Dictionary)


# ##           MANUAL COMMAND         ## #
@app.route('/api/manualdemand', methods=['POST'])
def receive_manual_demand():
    demanded = request.get_json()["demanded"]

    print("I received manual demand = " + str(demanded) + " %")
    print("Executing...")

    newPercentage = demand_motor(demanded)
    print("Executed = " + str(math.floor(newPercentage)))
    return jsonify({'realized': math.floor(newPercentage)})


# ##        GET REGULATION STATUS (AUTO/MANUAL)       ## #
@app.route('/api/getregulation', methods=['GET'])
def send_regulation():
    global status

    # retrieving regulation status from client
    regulation = status["regulation"]
    print("sending info on regulation type = " + regulation)
    if regulation == 'manual':
        return jsonify({'regulation': regulation,
                        'realized': status["percentageMotor"]})
    else:
        return jsonify({'regulation': regulation})


# ##        SET REGULATION STATUS (AUTO/MANUAL)       ## #
@app.route('/api/setregulation', methods=['POST'])
def receive_regulation():
    global status

    # retrieving regulation status from client
    regulation = request.get_json()["regulation"]
    print("I received the regulation type = " + regulation)

    # sanity check of the demanded status
    if (regulation != "auto" and regulation != "manual"):
        return jsonify({'error': 'unauthorized regulation mode: '
                        + '\'' + regulation + '\''
                        }), 400
    else:
        status["regulation"] = regulation
        return jsonify({'realized': regulation})


# ##        ROUTING       ## #
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    if app.debug:
        return requests.get('http://192.168.1.67/{}'.format(path)).text
    return render_template("index.html")


# ## ------------------------- ## #
# ## --        MEASURE      -- ## #
# ## ------------------------- ## #
def measure_temperature():
    return sensor.temperature


def measure_humidity():
    return sensor.relative_humidity


def get_measurement_history():
    return TimeAndTemp.query.all()


# ## ------------------------- ## #
# ## --        COMMAND      -- ## #
# ## ------------------------- ## #
def demand_motor(percentage):
    global status

    oldPercentage = status["percentageMotor"]
    newPercentage = motor.setPercentage(oldPercentage, percentage)
    status["percentageMotor"] = newPercentage

    return newPercentage


# ## ------------------------- ## #
# ## --     REGULATION      -- ## #
# ## ------------------------- ## #
def regulation(temperature, demand):
    return True


# ## ------------------------- ## #
# ## --  TEMPERATURE LOG    -- ## #
# ## ------------------------- ## #
class TimeAndTemp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.datetime.utcnow)
    temperature = db.Column(db.Float, unique=False, nullable=False)

    def __repr__(self):
        tempstr = "%.1f" % self.temperature
        return "\n<Time: " + tz.localize(self.time).__str__() + " // Temp. = " + tempstr + " °C>"


def RecordTemperature():
    fTemp = measure_temperature()
    T0 = TimeAndTemp(time=db.func.now(), temperature=fTemp)
    db.session.add(T0)
    db.session.commit()


# scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(func=RecordTemperature, trigger="interval", seconds=30)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

# ## ------------------------- ## #
# ## --        LAUNCH       -- ## #
# ## ------------------------- ## #
if __name__ == '__main__':
    global status

    temperature = measure_temperature()

    print("Starting... // temperature = " + str(temperature))
    # Motor checking for initPosition
    print("Motor intialization...")
    isOK = motor.initPosition()

    status = {
        'temperature': temperature,
        'regulation': 'auto',
        'percentageMotor': 0,
        'motorStatus': isOK
    }

    # app launch
    app.run()

    # Creation of database if not existing
    db.create_all()  # only to be created once
    RecordTemperature(temperature)

    # scheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=RecordTemperature, trigger="interval", seconds=30)
    scheduler.start()
