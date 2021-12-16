# This module maintains a queue and persistant history of tasks to pump water
# into a Smart Pot.
#
# The queue contains `PumpTask`s that have not been completed yet.
# The REST API enqueues new task. There is a background thread that
# dequeues and executes the tasks.
#
# The history is persistent and contains both completed and pending tasks.
# When a known pot connects, all pending pump tasks are enqueued. History
# entries are retained for at most a year.

import queue
import smartpot.persistance as persistance

# The maximum amount of water that can be pumped in a single task.
MAX_AMOUNT = 255

# The maximum age of a history entry in days before it should be removed from
# the database.
HISTORY_ENTRY_MAX_AGE = 365

# A Queue that contains the pending pump tasks.
pump_tasks = queue.Queue()


# A task for pumping water into a smart pot.
#
# This class is used both to represent a history entry that was fetched from
# the database and as a queue enetry.
#
# Usually you should not create an instance of this class directly.
# Use the functions defined in this module to fetch instances from the
# database or create new entries.
#
# A pending task has no `executed_at` timestamp.
# The `created_at` timestamp is automatically filled in by `add_history_entry`
# when the history entry for the task is created.
class PumpTask:
    def __init__(self, pot_id, amount, created_at=None, executed_at=None):
        self.pot_id = pot_id
        self.amount = min(amount, MAX_AMOUNT)
        self.created_at = created_at
        self.executed_at = executed_at


# Enqueues a new task for pumping the given amount of water into the smart pot
# with the given ID.
#
# A history entry for the task is automatically added to the database.
def enqueue_new_pump_task(pot_id, amount):
    task = PumpTask(pot_id, amount)
    add_history_entry(task)
    enqueue_pump_task(task)


# Enqueues a the a pump task that already has a history entry.
#
# This function is used for exmaple to put a pending task back into the queue
# after it has been restored from the database using `get_pending_tasks_of`.
def enqueue_pump_task(task):
    pump_tasks.put(task)


# Dequeues a task for pumping water into a smart pot that has not been executed
# yet.
#
# This method blocks until a pending task is available.
def dequeue_pump_task():
    while True:
        task = pump_tasks.get()

        # Do not execute tasks twice if they are enqueed twice (for example,
        # because the pot reconnected twice before the task was executed).
        if not has_executed_task(task):
            return task


# Gets the last pump task of the pot with the given id.
def get_last_task_of(pot_id):
    result = persistance.fetchone('''
        SELECT amount, created_at, executed_at FROM pump_history
        WHERE pot_id = ?
        ORDER BY created_at DESC
        LIMIT 1
    ''', (pot_id,))
    return None if result is None else PumpTask(pot_id, *result)


# Gets all pump task of the pot with the given id that have not been executed
# yet.
def get_pending_tasks_of(pot_id):
    tasks = persistance.fetchall('''
        SELECT amount, created_at FROM pump_history
        WHERE pot_id = ? AND executed_at IS NULL
        ORDER BY created_at ASC
    ''', (pot_id,))
    return [PumpTask(pot_id, amount, created_at) for amount, created_at in tasks]


# Adds a history entry for the given task.
#
# The `created_at` field of the pump task will be set to the current timestamp.
def add_history_entry(task):
    rowid = persistance.execute_insert('''
        INSERT INTO pump_history ( pot_id, amount )
        VALUES ( ?, ? )
    ''', (task.pot_id, task.amount))
    task.created_at = persistance.fetchone('''
        SELECT created_at FROM pump_history WHERE rowid = ?
    ''', (rowid,))[0]


# Sets the execution date of the given task to the current timestamp.
def set_task_execution_date(task):
    persistance.execute('''
        UPDATE pump_history SET executed_at = CURRENT_TIMESTAMP
        WHERE pot_id = ? AND created_at = ?
    ''', (task.pot_id, task.created_at))
    fetch_task_execution_date(task)


# Fetches the timestamp when the given task has been executed.
def fetch_task_execution_date(task):
    task.executed_at = persistance.fetchone('''
        SELECT executed_at FROM pump_history
        WHERE pot_id = ? AND created_at = ?
    ''', (task.pot_id, task.created_at))[0]


# Tests whether the database contains a history entry for the given task
# whose execution time has been set.
def has_executed_task(task):
    fetch_task_execution_date(task)
    return task.executed_at is not None


# Removes all history entries from the database that are older than
# `HISTORY_ENTRY_MAX_AGE` days.
def remove_old_history_entries():
    persistance.execute('''
        DELETE FROM pump_history WHERE created_at < datetime('now', ?)
    ''', (f'-{HISTORY_ENTRY_MAX_AGE} days',))
