# configure pytest


import pytest
from Finda import FdMultiController
import sqlite3
import helpers

# TODO: Add custom exception classes for testing

SEED = "INSERT INTO Asset VALUES  \
      ('RCK','Rock','CRYPTO'),  \
      ('BRY', 'Berry', 'CRYPTO'), \
      ('GLU', 'Glue', 'PETROLIUM DERIVATIVE'),  \
      ('EMY', 'EmptyAsset', 'CRYPTO');\
    INSERT INTO AssetClass VALUES \
        ('CRYPTO'), \
        ('PETROLIUM DERIVATIVE'), \
        ('EMTPTYCLASS');  \
    INSERT INTO AssetValue VALUES \
        ('RCK','2020-01-01','1.1','1.1','1.1','1.1',0), \
        ('RCK','2020-01-02','1.2','1.2','1.2','1.2',1), \
        ('BRY','2020-01-02','3.1','3.1','3.1','3.1',0), \
        ('GLU','2020-01-03','5.3','5.3','5.3','5.3',0); \
    INSERT INTO DividendPayout VALUES \
        ('RCK','2020-01-02','12.5'),  \
        ('RCK','2020-01-01','11.5'),  \
        ('BRY','2020-12-12','13.13'), \
        ('GLU','2020-12-20','1.1');"


@pytest.fixture(scope="function")
def db_controller():
    """ return db controller for use with testing
    """
    helpers.clear_DBs()
    FdMultiController.fd_create("__seeded_test_db__")
    FdMultiController.fd_create("__empty_test_db__")
    # this is a bit scetch but preferable to having a seeding script lying about
    # add some data independant of read and write modules

    conn1 = sqlite3.connect(FdMultiController._path_generator("__seeded_test_db__"))
    conn2 = sqlite3.connect(FdMultiController._path_generator("__empty_test_db__"))
    conn1.cursor().executescript(SEED)
    conn1.commit()
    conn2.commit()
    conn1.close()
    conn2.close()

    yield {
        "seeded": FdMultiController.fd_connect("__seeded_test_db__", "rwd"),
        "empty": FdMultiController.fd_connect("__empty_test_db__", "rwd"),
    }
    helpers.clear_DBs()
