from flask import Flask, request, render_template, jsonify
import random as rdm
from flask_cors import CORS
import requests
import time
import math

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


@app.route('/api/gettemperature', methods=['GET'])
def send_temperature():
    # demand = float(request.get_data('demanded'))
    time.sleep(0.5)
    return jsonify({'temperature': measure_temperature()})


@app.route('/api/manualdemand', methods=['POST'])
def receive_manual_demand():
    demanded = request.get_json()["demanded"]

    print("I received manual demand = " + str(demanded) + " %")
    time.sleep(0.5)
    return jsonify({'realized': math.floor(demanded)})


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
    return True


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
    status = {
        'temperature': -1,
        'regulation': 'auto'
    }
    print("je demarre // temperature = " + str(status["temperature"]))

    app.run()
