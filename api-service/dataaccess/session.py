import os

from databases import Database

try:
    database_url = os.environ["DATABASE_URL"]
except KeyError:
    raise RuntimeError("The DATABASE_URL environment variable is missing.")

database = Database(database_url)

async def connect():
    """
    This function initializes the database session for the current process.
    """
    await database.connect()

async def disconnect():
    """
    This function closes the database session for the current process.
    """
    await database.disconnect()

class _AbortTransaction(RuntimeError):
    pass

class Transaction():
    """
    Use this async context manager to execute a block of code in a transaction.
    """
    def __init__(self):
        self.rollback = False

    async def __aenter__(self):
        await database.execute("BEGIN;")
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if exc is not None:
            await database.execute("ROLLBACK;")
        else:
            await database.execute("COMMIT;")

        return exc_type is _AbortTransaction

    def abort(self):
        raise _AbortTransaction()
