import asyncio
import bleak
import bleak.backends.device
import smartpot.characteristics as characteristics

from typing import List

# The pots discovered during the last scan.
available_pots: List[bleak.backends.device.BLEDevice] = []


# Tests whether the given device advertised the smart pot service.
def has_smart_pot_service(device):
    return characteristics.SERVICE_UUID in device.metadata['uuids']


# Listens for advertisements of smart pot devices for the given duration in
# seconds.
async def scan(duration):
    global available_pots

    devices = await bleak.BleakScanner.discover(duration)
    available_pots = list(filter(has_smart_pot_service, devices))

    # Print addresses of available pots.
    s = ', '.join([device.address for device in available_pots])
    print('Available Pots: ' + s)


# Gets a list of all smart pots that were discovered during the last scan.
def get_available_pots():
    return available_pots.copy()
