"""
Test for the fd_read submodule of finda
"""

import pandas as pd

import helpers
import decimal as dec
import datetime as dt


def test_fd_read_read_asset_classes(db_controller):
    dfT = pd.DataFrame(
        [
            {"AssetClassName": "CRYPTO"},
            {"AssetClassName": "PETROLIUM DERIVATIVE"},
            {"AssetClassName": "EMTPTYCLASS"},
        ]
    )
    dfT.set_index("AssetClassName", inplace=True)
    dfR = db_controller["seeded"].read.read_asset_classes()
    helpers.compare_df(dfT, dfR)


def test_fd_read_read_assets(db_controller):
    # after updating functionality no longer expects assets with
    # no stored values to be returned (in this case empty asset)
    dfT = pd.DataFrame(
        [
            {"AssetClassName": "CRYPTO", "AssetTicker": "RCK", "Name": "Rock"},
            {"AssetClassName": "CRYPTO", "AssetTicker": "BRY", "Name": "Berry"},
            {
                "AssetClassName": "PETROLIUM DERIVATIVE",
                "AssetTicker": "GLU",
                "Name": "Glue",
            },
        ]
    )
    dfT.set_index("AssetTicker", inplace=True)
    dfR = db_controller["seeded"].read.read_assets()
    helpers.compare_df(dfT, dfR)


def test_fd_read_read_assets_in_class(db_controller):
    dfT = pd.DataFrame(
        [
            {"AssetClassName": "CRYPTO", "AssetTicker": "RCK", "Name": "Rock"},
            {"AssetClassName": "CRYPTO", "AssetTicker": "BRY", "Name": "Berry"},
        ]
    )
    dfT.set_index("AssetTicker", inplace=True)
    dfR = db_controller["seeded"].read.read_assets_in_class("CRYPTO")
    helpers.compare_df(dfT, dfR)
    empty_df = pd.DataFrame(columns=["AssetClassName", "Name", "AssetTicker"])
    empty_df.set_index(["AssetTicker"], inplace=True)
    # testing reading wierd asset names returns empty df
    helpers.compare_df(
        empty_df, db_controller["seeded"].read.read_assets_in_class("WiErAsSeT")
    )


def test_fd_read_read_assets_div_payout(db_controller):
    dfT = pd.DataFrame(
        [
            {
                "AssetTicker": "RCK",
                "PDate": pd.Timestamp(day=2, month=1, year=2020),
                "Payout": dec.Decimal("12.5"),
            },
            {
                "AssetTicker": "RCK",
                "PDate": pd.Timestamp(day=1, month=1, year=2020),
                "Payout": dec.Decimal("11.5"),
            },
            {
                "AssetTicker": "BRY",
                "PDate": pd.Timestamp(day=12, month=12, year=2020),
                "Payout": dec.Decimal("13.13"),
            },
        ]
    )
    dfT.set_index(["AssetTicker", "PDate"], inplace=True)
    dfR = db_controller["seeded"].read.read_assets_div_payout(["RCK", "BRY"])
    helpers.compare_df(dfT, dfR)
    # test empty
    empty_df = pd.DataFrame(columns=["AssetTicker", "Payout", "PDate"])
    empty_df.set_index(["AssetTicker", "PDate"], inplace=True)
    helpers.compare_df(
        empty_df, db_controller["seeded"].read.read_assets_div_payout([])
    )


def test_fd_read_read_asset_values(db_controller):
    dfT = pd.DataFrame(
        [
            {
                "AssetTicker": "RCK",
                "ADate": dt.date(day=2, month=1, year=2020),
                "ALow": dec.Decimal("1.2"),
                "AHigh": dec.Decimal("1.2"),
                "AOpen": dec.Decimal("1.2"),
                "AClose": dec.Decimal("1.2"),
                "IsInterpolated": 1,
            },
            {
                "AssetTicker": "GLU",
                "ADate": dt.date(day=3, month=1, year=2020),
                "ALow": dec.Decimal("5.3"),
                "AHigh": dec.Decimal("5.3"),
                "AOpen": dec.Decimal("5.3"),
                "AClose": dec.Decimal("5.3"),
                "IsInterpolated": 0,
            },
        ]
    )
    dfT.set_index(["AssetTicker", "ADate"], inplace=True)
    dfR = db_controller["seeded"].read.read_asset_values(
        ["RCK", "GLU"],
        dt.date(day=2, month=1, year=2020),
        dt.date(day=3, month=1, year=2020),
    )
    helpers.compare_df(dfT, dfR)
    dfT.reset_index(inplace=True)
    dfT = dfT.append(
        {
            "AssetTicker": "RCK",
            "ADate": dt.date(day=1, month=1, year=2020),
            "ALow": dec.Decimal("1.1"),
            "AOpen": dec.Decimal("1.1"),
            "AHigh": dec.Decimal("1.1"),
            "AClose": dec.Decimal("1.1"),
            "IsInterpolated": 0,
        },
        ignore_index=True,
    )
    dfT.set_index(["AssetTicker", "ADate"], inplace=True)
    # test open range
    dfR = db_controller["seeded"].read.read_asset_values(["RCK", "GLU"])
    helpers.compare_df(dfT, dfR)
    # test empty
    empty_df = pd.DataFrame(
        columns=[
            "ALow",
            "AOpen",
            "AHigh",
            "AClose",
            "IsInterpolated",
            "AssetTicker",
            "ADate",
        ]
    )
    empty_df.set_index(["AssetTicker", "ADate"], inplace=True)
    helpers.compare_df(empty_df, db_controller["seeded"].read.read_asset_values([]))
    # test wierd
    helpers.compare_df(
        empty_df, db_controller["seeded"].read.read_asset_values(["WiErDtIcKeR"])
    )
