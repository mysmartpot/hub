# This script can be used during debugging to create database entries for
# non-existing Smart Pots.

from smartpot.debug.fake_pots import fake_pot_addrs, fake_plant_names
import smartpot.known_pots as known_pots
import smartpot.persistance as persistance

# Create database entries for fake pots.
for addr, name in zip(fake_pot_addrs, fake_plant_names):
    known_pots.add_known_pot(addr, name)
    print(f'Added {addr} to database')

# Shutdown the persistance thread such that the script can exit.
persistance.worker.shutdown()
