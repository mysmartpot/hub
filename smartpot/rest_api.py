from flask import Flask, abort, request
from flask_json import FlaskJSON, as_json

import smartpot.available_pots as available_pots
import smartpot.known_pots as known_pots
import smartpot.pump_tasks as pump_tasks
import smartpot.measurements as measurements
import smartpot.connected_pots as connected_pots

# Initialize Flask application.
api = Flask('smart-pot-api')
json = FlaskJSON(api)

# Configure Flask JSON.
api.config['JSON_ADD_STATUS'] = False

# Create an HTTP response for routes without content.
no_content_response = ('', 204)


# Gets the IDs and display names of all known pots.
#
# Returns a JSON array of objects with the following fields.
#
#     {
#       "id": string,
#       "name": string,
#     }
@api.route('/api/pots')
@as_json
def get_pots():
    return [{
        'id': id,
        'name': name
    } for id, name in known_pots.get_known_pot_names().items()]


# Gets the address and signal strength of all visible pots that are unknown.
#
# Returns a JSON object with the following fields.
#
#     {
#       "addr": string,
#       "rssi": number
#     }
@api.route('/api/pots/available')
@as_json
def get_available_pots():
    return [{
        'addr': device.address,
        'rssi': device.rssi,
    } for device in available_pots.get_available_pots()]


# Adds an available pot to the list of known pots.
#
# Expects the request body to contain the BLE address of the pot to add and the
# display name for the new pot as a JSON object with the following fields.
#
#     {
#       "addr": string,
#       "name": string
#     }
#
# Returns a JSON object that contains the ID of the added pot.
#
#     {
#       "id": string
#     }
@api.route('/api/pots', methods=['POST'])
@as_json
def add_pot():
    # Check that all required fields are passed in the request body.
    if (not isinstance(request.json, dict)
            or 'addr' not in request.json
            or 'name' not in request.json):
        abort(400)

    # Extract fields from request body.
    addr = request.json['addr']
    name = request.json['name']

    # Check type of the fields.
    if not isinstance(addr, str) or not isinstance(name, str):
        abort(400)

    # Add pot to database
    id = known_pots.add_known_pot(addr, name)
    return {
        "id": id
    }


# Gets the status, latest measurements and commands of the known pot with the
# given ID.
#
# Returns a JSON object with the following fields.
#
#     {
#       "online": boolean,
#       "measurement": {
#         "soil-moisture": number,
#         "water-level": number,
#         "timestamp": timestamp
#       },
#       "watered": {
#         "amount": number,
#         "time": timestamp,
#         "completed": boolean
#       },
#     }
#
# If there is no `measurement` yet, the corresponding field is set to `null`.
@api.route('/api/pot/<int:id>', methods=['GET'])
@as_json
def get_pot(id):

    addr = known_pots.lookup_known_pot_addr(id)
    measurement = measurements.get_last_measurement(id)
    last_pump_task = pump_tasks.get_last_task_of(id)

    return {
        'online': connected_pots.is_connected(addr),
        'measurement': None if measurement is None else {
            'soil-moisture': measurement.soil_moisture,
            'water-level': measurement.water_level,
            'timestamp': measurement.timestamp,
        },
        'watered': None if last_pump_task is None else {
            'amount': last_pump_task.amount,
            'timestamp': next(timestamp for timestamp in [
                last_pump_task.executed_at, last_pump_task.created_at
            ] if timestamp is not None),
            'completed': last_pump_task.executed_at is not None,
        }
    }


# Renames the known pot with the given ID.
#
# Expects the request body to contain the new name of the pot as a JSON
# object with the following format.
#
#     {
#       "name": string
#     }
#
# Returns an HTTP response without content.
@api.route('/api/pot/<int:id>', methods=['PUT'])
def rename_pot(id):
    # Check that all required fields are passed in the request body.
    if not isinstance(request.json, dict) or 'name' not in request.json:
        abort(400)

    # Extract fields from request body.
    name = request.json['name']

    # Check type of the fields.
    if not isinstance(name, str):
        abort(400)

    known_pots.rename_known_pot(id, name)
    return no_content_response


# Queues a command to water the connected pot with the given ID.
#
# Expects the request body to contain the amount of water as a JSON
# object with the following format.
#
#       {
#          "amount": number
#       }
#
# Returns an HTTP response without content.
@api.route('/api/pot/<int:id>/water', methods=['POST'])
@as_json
def water_pot(id):
    # Check that all required fields are passed in the request body.
    if not isinstance(request.json, dict) or 'amount' not in request.json:
        abort(400)

    # Extract fields from request body.
    amount = request.json['amount']

    # Check type of the fields.
    if not isinstance(amount, int) or amount >= pump_tasks.MAX_AMOUNT:
        abort(400)

    # Check that there is no pending task.
    last_pump_task = pump_tasks.get_last_task_of(id)
    if last_pump_task is not None and last_pump_task.executed_at is None:
        abort(409)

    # Water the pot with the given ID.
    pump_tasks.enqueue_new_pump_task(id, amount)

    return no_content_response


# Removes the known pot with the given ID.
#
# If the pot is currently connected, it is disconnected.
#
# Returns an HTTP response without content.
@api.route('/api/pot/<int:id>', methods=['DELETE'])
@as_json
def remove_pot(id):
    addr = known_pots.lookup_known_pot_addr(id)
    known_pots.remove_known_pot(id)
    connected_pots.disconnect(addr)
    return no_content_response


# Runs the REST API and passes the given arguments to Flask.
def run(*args, **kw_args):
    print('starting API...')
    api.run(*args, **kw_args)


# When the script is invoked directly, start the REST API in debug mode.
if __name__ == '__main__':
    run(debug=True)
