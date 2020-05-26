import pandas as pd
import helpers
import datetime as dt
import decimal as dec


def test_delete_values(db_controller):

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

    db_controller["seeded"].remove.deleteValues("BRY", "2020-01-02")
    db_controller["seeded"].remove.deleteValues("RCK", "2020-01-01")
    dfR = db_controller["seeded"].read.read_asset_values(
        ["RCK", "GLU", "BRY"],
        dt.date(day=1, month=1, year=2020),
        dt.date(day=3, month=1, year=2020),
    )
    helpers.compare_df(dfT, dfR)


def test_delete_assets(db_controller):
    """
    Test if deleteAsset method works
    """
    dfT = pd.DataFrame(
        [
            {"AssetClassName": "CRYPTO", "AssetTicker": "RCK", "Name": "Rock"},
            {"AssetClassName": "CRYPTO", "AssetTicker": "BRY", "Name": "Berry"},
        ]
    )
    dfT.set_index("AssetTicker", inplace=True)
    db_controller["seeded"].remove.deleteAssets("GLU")
    dfR = db_controller["seeded"].read.read_assets()
    helpers.compare_df(dfT, dfR)


def test_delete_assetclass(db_controller):
    """
    Test if deleteAssetclass method works
    """
    dfT = pd.DataFrame(
        [{"AssetClassName": "PETROLIUM DERIVATIVE"}, {"AssetClassName": "EMTPTYCLASS"}]
    )
    dfT.set_index("AssetClassName", inplace=True)
    db_controller["seeded"].remove.deleteAssetClasses("CRYPTO")
    dfR = db_controller["seeded"].read.read_asset_classes()
    helpers.compare_df(dfT, dfR)


def test_delete_div(db_controller):
    """
    Test if deletediv method works
    """
    dfT = pd.DataFrame(
        [
            {
                "AssetTicker": "RCK",
                "PDate": dt.date(day=2, month=1, year=2020),
                "Payout": dec.Decimal("12.5"),
            },
            {
                "AssetTicker": "RCK",
                "PDate": dt.date(day=1, month=1, year=2020),
                "Payout": dec.Decimal("11.5"),
            },
            {
                "AssetTicker": "BRY",
                "PDate": dt.date(day=12, month=12, year=2020),
                "Payout": dec.Decimal("13.13"),
            },
        ]
    )
    dfT.set_index(["AssetTicker", "PDate"], inplace=True)
    db_controller["seeded"].remove.delete_div_payouts("GLU")
    dfR = db_controller["seeded"].read.read_assets_div_payout(["RCK", "BRY", "GLU"])
    helpers.compare_df(dfT, dfR)
