# This is the main module of the Smart Pot Hub.
#
# This module runs multiple threads to manage the connected Smart Pot
# divices and starts the REST API.

import asyncio
import smartpot.available_pots as available_pots
import smartpot.characteristics as characteristics
import smartpot.connected_pots as connected_pots
import smartpot.known_pots as known_pots
import smartpot.measurements as measurements
import smartpot.pump_tasks as pump_tasks
import smartpot.rest_api as rest_api
import threading
import traceback


# A thread that manages the connection to the Smart Pots.
#
# This thread periodically scans for available Smart Pots. If a known Smart Pot
# is available, a connection is established and we start to listen for
# measurements and run pending pump tasks.
class ConnectionThread (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.deamon = True
        self.event_loop = asyncio.new_event_loop()

    def run(self):
        asyncio.set_event_loop(self.event_loop)
        self.event_loop.run_until_complete(self.loop())

    # Main loop of the thread.
    async def loop(self):
        while True:
            try:
                await self.run_scan()
                await self.run_connect()
            except Exception as e:
                print(f'Error: {e}')
                traceback.print_exc()

    # Scans to find available pots.
    async def run_scan(self):
        await available_pots.scan(10.0)

    # Connects to available known pots.
    async def run_connect(self):
        for device in available_pots.get_available_pots():
            # Try to connect if the pot is known.
            if known_pots.is_pot_known_addr(device.address):
                pot_id = known_pots.lookup_known_pot_id(device.address)
                client = await connected_pots.connect(device)
                if client is None:
                    continue

                # Enable notifications for the soil moisture and water level
                # characteristics.
                def on_measurements(data):
                    measurements.add_measurement(pot_id, *data)
                await characteristics.subscribe_measurements(client, on_measurements)

                # Enqueue pump tasks for the pot that have not been completed
                # yet because the pot was not connected when the task was
                # created.
                for task in pump_tasks.get_pending_tasks_of(pot_id):
                    pump_tasks.enqueue_pump_task(task)


connectionThread = ConnectionThread()
connectionThread.start()


# A thread that blocks until a new pump task is scheduled and then runs that
# task in the `connectThread`s event loop.
class PumpThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.deamon = True

    def run(self):
        # Executes the given pump task.
        async def run_task(task):
            addr = known_pots.lookup_known_pot_addr(task.pot_id)
            if connected_pots.is_connected(addr):
                client = connected_pots.get_pot_by_addr(addr)
                await characteristics.write_pump_amount(client, task.amount)
                pump_tasks.set_task_execution_date(task)

        # Run pump tasks in the event loop of the `connectionThread`.
        while True:
            task = pump_tasks.dequeue_pump_task()
            coro = run_task(task)
            asyncio.run_coroutine_threadsafe(coro, connectionThread.event_loop)


pumpThread = PumpThread()
pumpThread.start()


# Removes old database entries once per day.
def run_periodic_cleanup():
    measurements.remove_old_measurements()
    pump_tasks.remove_old_history_entries()

    SECONDS_PER_DAY = 24 * 60 * 60
    threading.Timer(SECONDS_PER_DAY, run_periodic_cleanup).start()


run_periodic_cleanup()

# Run the REST API in the main thread.
rest_api.run(host="0.0.0.0")
