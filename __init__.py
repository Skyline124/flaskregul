from flask import Flask, request, render_template, jsonify

from flask_cors import CORS

import sys, time, math, requests
import random as rdm

sys.path.append('backend')
import motor as motor

# status = {
#     'temperature': -1,
#     'regulation': 'auto'
# }

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

    if isOK == "OK":
        return jsonify({'motorStatus': isOK})
    else:
        return jsonify({'motorStatus': isOK}), 500


@app.route('/api/gettemperature', methods=['GET'])
def send_temperature():
    # demand = float(request.get_data('demanded'))
    time.sleep(0.5)
    return jsonify({'temperature': measure_temperature()})


@app.route('/api/manualdemand', methods=['POST'])
def receive_manual_demand():
    demanded = request.get_json()["demanded"]

    print("I received manual demand = " + str(demanded) + " %")
    print("Executing...")

    newPercentage = demand_motor(demanded)
    print("Executed = " + str(math.floor(newPercentage)))
    return jsonify({'realized': math.floor(newPercentage)})


@app.route('/api/setregulation', methods=['POST'])
def receive_regulation():
    global status

    # retrieving regulation status from client
    regulation = request.get_json()["regulation"]
    print("I received the regulation type = " + regulation)
    time.sleep(0.5)
    print("sleep ended")

    # sanity check of the demanded status
    if (regulation != "auto" and regulation != "manual"):
        return jsonify({
            'error': 'unauthorized regulation mode: '
            + '\'' + regulation + '\''
            }), 400
    else:
        status["regulation"] = regulation
        return jsonify({'realized': regulation})


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    if app.debug:
        return requests.get('http://127.0.0.1:5000/{}'.format(path)).text
    return render_template("index.html")


# ## ------------------------- ## #
# ## --        MEASURE      -- ## #
# ## ------------------------- ## #
def measure_temperature():
    return 16 + 14*rdm.random()


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
