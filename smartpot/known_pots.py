# This module contains functions to interact with the persistant `known_pots`
# table.
#
# A known pot is a Smart Pot that has been connected to the Hub in the past.
# There is a background thread that ensures that known pots connect
# automatically as soon as they become available.

import smartpot.persistance as persistance


# Gets the address of the known pot with the given ID.
def lookup_known_pot_addr(id):
    return persistance.fetchone('''
        SELECT addr FROM known_pots WHERE id = ?
    ''', (id,))[0]


# Gets the id of the known pot with the given address.
def lookup_known_pot_id(addr):
    return persistance.fetchone('''
        SELECT id FROM known_pots WHERE addr = ?
    ''', (addr,))[0]


# Tests whether the pot with the given address is known.
def is_pot_known_addr(addr):
    return persistance.fetchone('''
        SELECT EXISTS (SELECT id FROM known_pots WHERE addr = ?)
    ''', (addr,))[0] == 1


# Gets a dictionary that maps the IDs of all known pots to their display name.
def get_known_pot_names():
    return dict(persistance.fetchall('SELECT id, name FROM known_pots'))


# Adds a pot with the given BLE address and display name.
#
# Returns the ID of the added pot.
def add_known_pot(addr, name):
    return persistance.execute_insert('''
        INSERT INTO known_pots ( addr, name ) VALUES ( ?, ? )
    ''', (addr, name))


# Renames the pot with the given ID.
def rename_known_pot(id, name):
    persistance.execute('''
        UPDATE known_pots SET name = ? WHERE id = ?
    ''', (name, id))


# Removes the pot with the given ID from the database.
def remove_known_pot(id):
    persistance.execute('''
        DELETE FROM known_pots WHERE id = ?
    ''', (id,))
