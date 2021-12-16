import random
import smartpot.known_pots as known_pots
import smartpot.measurements as measurements
import smartpot.persistance as persistance
from smartpot.debug.fake_pots import fake_pot_addrs

random.seed()

for addr in fake_pot_addrs:
    id = known_pots.lookup_known_pot_id(addr)
    soil_moisture = random.randint(0, 1023)
    water_level = random.randint(0, 1023)
    measurements.add_measurement(id, soil_moisture, water_level)
    print(f'Added measurement for {addr} to database')

persistance.worker.shutdown()
