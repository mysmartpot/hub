# This module provides methods to manage the Bluetooth connection to Smart Pots.

import bleak
from bleak.exc import BleakError

from typing import Dict

# Dictionary that maps addresses to the `BleakClient` of connected smart pots.
connected_pots: Dict[str, bleak.BleakClient] = {}


# Connects to a discovered smart pot device.
#
# If the connection to the device is loost, the connection is closed
# automatically via the `on_disconnected` callback.
async def connect(device):
    if not is_connected(device.address):
        try:
            client = bleak.BleakClient(device)
            client.set_disconnected_callback(on_disconnected)
            await client.connect()
            connected_pots[client.address] = client
            print(f'Connected to {client.address}!')
            return client
        except BleakError:
            print(f'Failed to connect to {client.address}!')


# Callback that is invoked when a connected device disconnects unsolicited.
# Removes the device from the dictionary of connected devices.
def on_disconnected(client):
    if is_connected(client.address):
        del connected_pots[client.address]
        print(f'Lost connection to {client.address}!')


# Disconnects from the smart pot with the given address.
#
# If the device is out of range, it will disconnect automatically. This
# function only needs to be called to disconnect from a pot that has been
# removed from the list of known pots.
#
# If the device is not connected, this function has no effect.
async def disconnect(addr):
    if is_connected(addr):
        client = connected_pots.pop(addr)
        await client.disconnect()
        print(f'Disconnected from {client.address}!')


# Tests whether there is an active connection to the smart pot with the given
# address.
def is_connected(addr):
    return addr in connected_pots


# Gets the `BleakClient` instance for the connected smart pot's given address.
def get_pot_by_addr(addr):
    return connected_pots[addr]


# Gets a dictionary that maps the addrsses of all connected smart pot to the
# corresponding `BleakClient` instance.
def get_connected_pots():
    return connected_pots.copy()
