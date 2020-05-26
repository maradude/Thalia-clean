"""
Module containing methods for reading from financial data database
"""
import pandas as pd
import sqlite3
from decimal import Decimal


class FdRead:
    def __init__(self, db_address):
        self.db_address = db_address

    def read_asset_values(self, asset_tickers, startDate=None, endDate=None):
        """Get all values of list of assets in date range

        Args:
        assetTickers: List[String] | Names of asset tickers
        startDate: datetime.Date | lower bound on date
        endDate: datetime.Date | upper bound on date

        Return:
        Pandas dataframe of format:
        {Columns: [AOpen<Decimal.decimal>, AClose<Decimal.decimal>,
                   AHigh<Decimal.decimal>, ALow<Decimal.decimal>]
         Index: [AssetTicker<String>, ADate <datetime.date>]}
        containing AssetValues with date between start and end date and assetTicker
        in assetTickers
        """
        # cast asset_tickers to list ensure appending works
        asset_tickers = list(asset_tickers)
        # Optionally move name to seperate config file later
        conn = sqlite3.connect(self.db_address)
        # generate parameter list for subsitution
        generated_params = "(" + ",".join(["?"] * len(asset_tickers)) + ")"

        # construct query
        query = (
            "SELECT * \
                 FROM AssetValue \
                 WHERE AssetValue.AssetTicker IN "
            + generated_params
            + " "
        )
        if startDate is not None:
            query += "AND (AssetValue.ADate >= ?) "
            asset_tickers.append(str(startDate))
        if endDate is not None:
            query += "AND (AssetValue.ADate <= ?) "
            asset_tickers.append(str(endDate))
        # read data into df
        df0 = pd.read_sql(query + ";", conn, params=asset_tickers)
        conn.close()
        # fix types
        df0["AOpen"] = df0["AOpen"].map(Decimal)
        df0["AClose"] = df0["AClose"].map(Decimal)
        df0["AHigh"] = df0["AHigh"].map(Decimal)
        df0["ALow"] = df0["ALow"].map(Decimal)
        df0["ADate"] = pd.to_datetime(df0["ADate"], format="%Y-%m-%d %H:%M:%S")
        df0.set_index(["AssetTicker", "ADate"], inplace=True)
        return df0

    def read_assets(self):
        """Get records of all financial assets stored in db that have associated asset values

        Args:
        None

        Return:
        Pandas dataframe of format
        {Columns: [Name<String>, AssetClassName<String>]
                   Index: [AssetTicker<String>]}
        each row containing details of an asset
        currently saved in db

        Notes:
        Will only return assets that have associated asset values stored in AssetValues table
        If nothing stored will return empty dataframe of same format
        """
        # Optionally move name to seperate config file later
        conn = sqlite3.connect(self.db_address)
        # read data in df
        df0 = pd.read_sql(
            "SELECT * \
         FROM Asset WHERE Asset.AssetTicker IN (SELECT AssetTicker FROM AssetValue)",
            conn,
        )
        conn.close()
        # adjust index if neccesary
        df0.set_index("AssetTicker", inplace=True)
        return df0

    def read_assets_in_class(self, asset_class):
        """Get records of all assets in an asset class with values in AssetValues

        Args:
        assetClass: string | Name of asset class

        Return:
        Pandas dataframe of format
        {Columns: [Name<String>, AssetClassName<@assetClass>]
                   Index: [AssetTicker<String>]}
        each row containing details of an asset
        currently saved in db with asset class equal to assetClass

        Notes:
        - Will only return assets that have asset values stored in AssetValues table

        - If assetClass not in database, return empty dataframe in format

        - Will return AssetClass row in dataframe despite all values being equal
        (this is so dataframe can be used with fdWrite library methods as-is)

        - Implements seperate query to getAssetClasses due to performance
        considerations (Large number of assets should not be in working memory
        unless needed)
        """
        # Optionally move name to seperate config file later
        conn = sqlite3.connect(self.db_address)
        # read data in df
        df0 = pd.read_sql(
            "SELECT * \
         FROM Asset \
         WHERE Asset.AssetClassName = $className AND Asset.AssetTicker IN (SELECT AssetTicker FROM AssetValue);",
            conn,
            params={"className": asset_class},  # use params dict to sanitize input
        )
        conn.close()
        # adjust index if neccesary
        df0.set_index("AssetTicker", inplace=True)
        return df0

    def read_assets_div_payout(self, asset_tickers):
        """Get record of all divident payouts for specific asset

        Args:
        asset_tickers: list of strings of asset tickers | asset ticker

        Return:
        Pandas dataframe of format
        {Columns: [Payout<decima.Decimal>]
                   Index: [AssetTicker<String>, PDate<datetime.date>]}

        Notes:
        - If assetTicker not in database, return empty dataframe in format

        - Will return AssetTicker row in dataframe despite all values being equal
        (this is so dataframe can be used with fdWrite library methods as-is)
        """
        # Optionally move name to seperate config file later
        conn = sqlite3.connect(self.db_address)
        generated_params = "(" + ",".join(["?"] * len(asset_tickers)) + ")"

        # construct query
        query = (
            "SELECT * \
                 FROM DividendPayout \
                 WHERE DividendPayout.AssetTicker IN "
            + generated_params
            + " "
        )
        # read data into df
        df0 = pd.read_sql(query + ";", conn, params=asset_tickers)
        conn.close()

        df0["Payout"] = df0["Payout"].map(Decimal)
        df0["PDate"] = pd.to_datetime(df0["PDate"], format="%Y-%m-%d %H:%M:%S")

        df0.set_index(["AssetTicker", "PDate"], inplace=True)
        return df0

    def read_asset_classes(self):
        """Get records of all asset classes stored in fin database

        Args:
        None

        Return:
        Pandas dataframe of format
        {Columns: [] Index: [AssetClassName<String>]}
        each row containing details of an assetClass
        currently stored in db

        Notes:
        If nothing stored will return empty dataframe of same format
        """
        # Optionally move name to seperate config file later
        conn = sqlite3.connect(self.db_address)
        # read data in df
        df0 = pd.read_sql(
            "SELECT * \
         FROM AssetClass",
            conn,
        )
        conn.close()
        # adjust index if neccesary
        df0.set_index("AssetClassName", inplace=True)
        return df0
