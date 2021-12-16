import mvar
import queue
import sqlite3
import threading


# A thread that performs all database operations.
class WorkerThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.deamon = True
        self.name = 'Database Worker Thread'
        self._queue = queue.Queue()
        self._isRunning = True

    # Enqueues a task to be executed by the worker thread and blocks until
    # the task completes.
    def await_task(self, task):
        result_var = mvar.MVar()
        self._queue.put((task, result_var))
        result, is_error = result_var.take()
        if is_error:
            raise result
        return result

    def shutdown(self):
        def task(_):
            print(f'Shutting down {self.name}...')
            self._isRunning = False
        print(f'Waiting to shut down {self.name}...')
        self.await_task(task)

    def run(self):
        # Connect to database.
        print(f'Started {self.name}')
        with sqlite3.connect('smart-pot.db') as connection:
            cursor = connection.cursor()

            # Execute enqueued tasks.
            while self._isRunning:
                try:
                    task, result_var = self._queue.get()
                    result = task(cursor)
                    result_var.put((result, False))
                except Exception as e:
                    result_var.put((e, True))


worker = WorkerThread()
worker.start()

# Calls the given callback with a new cursor and saves the changes if the
# callback completes without throwing an exception. Otherwise, the transaction
# is rolled back and the exception is rethrown.
def transaction(callback):
    def task(cursor):
        try:
            result = callback(cursor)
            cursor.connection.commit()
            return result
        except Exception:
            cursor.connection.rollback()
            raise
    return worker.await_task(task)


# Executes the given query and fetches the first result.
def fetchone(query, args=()):
    return worker.await_task(lambda c: c.execute(query, args).fetchone())


# Executes the given query and fetches all results.
def fetchall(query, args=()):
    return worker.await_task(lambda c: c.execute(query, args).fetchall())


# Executes the given query and saves the changes if it completes sucessfully.
def execute(query, args=()):
    return transaction(lambda c: c.execute(query, args))


# Executes the given insert query, saves the changes and returns the ID of the
# inserted row.
def execute_insert(query, args=()):
    return execute(query, args).lastrowid


# Initializes the database if the tables do not exist.
def create_tables(cursor):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS known_pots (
            id    INTEGER  NOT NULL  PRIMARY KEY  AUTOINCREMENT,
            addr  TEXT     NOT NULL  UNIQUE,
            name  TEXT     NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS measurements (
            pot_id         INTEGER    NOT NULL,
            soil_moisture  INTEGER    NOT NULL,
            water_level    INTEGER    NOT NULL,
            timestamp      TIMESTAMP  NOT NULL  DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY ( pot_id, timestamp ),
            FOREIGN KEY ( pot_id ) REFERENCES known_pots ( id )
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pump_history (
            pot_id       INTEGER    NOT NULL,
            amount       INTEGER    NOT NULL,
            created_at   TIMESTAMP  NOT NULL  DEFAULT CURRENT_TIMESTAMP,
            executed_at  TIMESTAMP            DEFAULT NULL,
            PRIMARY KEY ( pot_id, created_at ),
            FOREIGN KEY ( pot_id ) REFERENCES known_pots ( id )
        )
    ''')


transaction(create_tables)
