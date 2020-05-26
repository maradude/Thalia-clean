"""
Test for the fd_read submodule of Finda
"""
import pytest
import pandas as pd
import helpers
import decimal as dec
import datetime as dt
import sqlite3

"""
NOTE FROM A WARY WIZARD:
tests generic method for generating queries, the only variable differing between
this and subsequent calls is the name of the table to witch to write the query.
If the name of the table is misspelt in the methods, the tests will pass but no
data will be written. Generating tests for this with the modules current layout
would be incredibly time consuming, so in the interest of time the author has
decided to ommit them in favour of this warning. In future I will take
greater care to design with testing in mind from the ground up.

You have been warned ...
"""


def test_generic_format_checker(db_controller):
    df0 = pd.DataFrame(columns=["testCol", "testID"])
    df0.set_index("testID", inplace=True)
    db_controller["empty"].write.t_check_df_format(df0, ["testCol", "testID"])
    with pytest.raises(Exception):
        db_controller["empty"].write.t_check_df_format(df0, ["WiErDvAlUe", "testID"])
        pytest.fail("expected error when inserting df with invalid columns")


def test_exeption_query_generator(db_controller):
    with pytest.raises(sqlite3.OperationalError):
        db_controller["empty"].write.t_insert_df(pd.DataFrame(), "WiErDtAbLe")
        pytest.fail("expected error instering into invalid table")


def test_fd_write_write_asset_classes(db_controller):
    ac = db_controller["seeded"].read.read_asset_classes()
    db_controller["empty"].write.write_asset_classes(ac)
    # test replace
    db_controller["empty"].write.write_asset_classes(ac)
    helpers.compare_df(db_controller["empty"].read.read_asset_classes(), ac)


def test_fd_write_write_assets(db_controller):
    od = pd.DataFrame(
        [{"AssetClassName": "CRYPTO", "AssetTicker": "RCK", "Name": "Rock"}]
    )
    od.set_index("AssetTicker", inplace=True)
    # test foreign key constraint
    with pytest.raises(sqlite3.IntegrityError):
        db_controller["empty"].write.write_assets(od)
        pytest.fail("expected error inserting non existing asset class")
    db_controller["seeded"].write.write_assets(od)


def test_fd_write_write_asset_values(db_controller):
    od = pd.DataFrame(
        [
            {
                "AssetTicker": "RCK",
                "ADate": dt.date(day=3, month=1, year=2020),
                "ALow": dec.Decimal("1.2"),
                "AHigh": dec.Decimal("1.2"),
                "AOpen": dec.Decimal("1.2"),
                "AClose": dec.Decimal("1.2"),
                "IsInterpolated": 1,
            }
        ]
    )
    od.set_index(["AssetTicker", "ADate"], inplace=True)
    db_controller["seeded"].write.write_asset_values(od)
    # test foreign key constraint
    with pytest.raises(sqlite3.IntegrityError):
        db_controller["empty"].write.write_asset_values(od)
        pytest.fail("expected error inserting non existing asset")
    db_controller["seeded"].write.write_asset_values(od)


def test_fd_write_write_dividend_payouts(db_controller):
    od = pd.DataFrame(
        [
            {
                "AssetTicker": "RCK",
                "PDate": dt.date(day=10, month=1, year=2020),
                "Payout": dec.Decimal("12.5"),
            }
        ]
    )
    od.set_index(["AssetTicker", "PDate"], inplace=True)
    with pytest.raises(sqlite3.IntegrityError):
        db_controller["empty"].write.write_dividend_payouts(od)
        pytest.fail("expected error inserting non existing asset")
    db_controller["seeded"].write.write_dividend_payouts(od)
