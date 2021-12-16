# This module defines the Bluetooth characteristics that are used to
# communicate with the Smart Pot devices.
#
# There are two characteristics: one to read measurement data and one to
# control the pump relay. To avoid polling the measurement characteristics
# notifications can be used (see `subscribe_measurements`).

# The UUID of the smart pot service.
SERVICE_UUID = 'b62a0000-069a-4fc6-9d5b-1daadc0cda33'

# The UUID of the soil moisture and water level sensor characteristic.
MEASUREMENTS_UUID = 'b62a0001-069a-4fc6-9d5b-1daadc0cda33'

# The UUID of the pump relay characteristic.
PUMP_AMOUNT_UUID = 'b62a0002-069a-4fc6-9d5b-1daadc0cda33'


# Decodes the value of the soi moisture and water level characteristic.
def decode_measurements(byte_value):
    soil_moisture = int.from_bytes(byte_value[0:2], byteorder='little')
    water_level = int.from_bytes(byte_value[2:4], byteorder='little')
    return soil_moisture, water_level


# Reads the soil moisture and water level characteristic of the given connected
# pot and returns a future of the result.
#
# The result is a tuple where the first element is the soil moisture
# measurement and the second value is the water level measurement.
async def read_measurements(client):
    byte_value = await client.read_gatt_char(MEASUREMENTS_UUID)
    return decode_measurements(byte_value)


# Enables notifications for the soil moisture and water level characteristic
# of the give connected pot.
async def subscribe_measurements(client, callback):
    def listener(sender, data):
        measurements = decode_measurements(data)
        callback(measurements)
    await client.start_notify(MEASUREMENTS_UUID, listener)


# Writes into the pump relay characteristic of the given connected pot
# and waits for a response.
async def write_pump_amount(client, amount):
    byte_value = amount.to_bytes(1, byteorder='little')
    await client.write_gatt_char(PUMP_AMOUNT_UUID, byte_value, True)
