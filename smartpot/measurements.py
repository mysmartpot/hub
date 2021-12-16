import smartpot.persistance as persistance

# The maximum age of a measurement in days before it should be removed from the
# database.
MEASUREMENT_MAX_AGE = 365


# The result type of `get_last_measurement`.
class Measurement:
    def __init__(self, soil_moisture, water_level, timestamp):
        self.soil_moisture = soil_moisture
        self.water_level = water_level
        self.timestamp = timestamp


# Inserts a measurement into the database.
def add_measurement(pot_id, soil_moisture, water_level):
    persistance.execute_insert('''
        INSERT INTO measurements ( pot_id, soil_moisture, water_level )
                          VALUES ( ?, ?, ? )
    ''', (pot_id, soil_moisture, water_level))


# Finds the latest recorded measurement of the given pot.
def get_last_measurement(pot_id):
    result = persistance.fetchone('''
        SELECT soil_moisture, water_level, timestamp
        FROM measurements
        WHERE pot_id = ?
        ORDER BY timestamp DESC
        LIMIT 1
    ''', (pot_id,))
    return None if result is None else Measurement(*result)


# Removes all measurements from the database that are older than
# `MEASUREMENT_MAX_AGE` days.
def remove_old_measurements():
    persistance.execute('''
        DELETE FROM measurements WHERE timestamp < datetime('now', ?)
    ''', (f'-{MEASUREMENT_MAX_AGE} days',))
