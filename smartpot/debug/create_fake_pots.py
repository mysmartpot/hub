import smartpot.known_pots as known_pots
from smartpot.debug.fake_pots import fake_pot_addrs, fake_plant_names

for addr, name in zip(fake_pot_addrs, fake_plant_names):
    known_pots.add_known_pot(addr, name)
    print(f'Added {addr} to database')

persistance.worker.shutdown()
