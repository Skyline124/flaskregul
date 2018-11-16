from flask import Flask, request, render_template, jsonify
from flask_cors import CORS

import time
import math
import requests
import random as rdm
from backend import motor as motor
import board
import busio
import adafruit_sht31d

i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_sht31d.SHT31D(i2c)


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
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


@app.route('/api/random')
def random_number():
    response = {
        'randomNumber': rdm.randint(1, 100)
    }
    return jsonify(response)


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


@app.route('/api/gettemperature', methods=['GET'])
def send_temperature():
    # demand = float(request.get_data('demanded'))

    return jsonify({'temperature': measure_temperature()})


@app.route('/api/gethumidity', methods=['GET'])
def send_humidity():
    # demand = float(request.get_data('demanded'))

    return jsonify({'humidity': measure_humidity()})


@app.route('/api/manualdemand', methods=['POST'])
def receive_manual_demand():
    demanded = request.get_json()["demanded"]

    print("I received manual demand = " + str(demanded) + " %")
    print("Executing...")

    newPercentage = demand_motor(demanded)
    print("Executed = " + str(math.floor(newPercentage)))
    return jsonify({'realized': math.floor(newPercentage)})


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

    app.run()

