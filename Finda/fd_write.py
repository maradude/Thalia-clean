"""
Module containing methods for writing to financial database

#TODO: account for column order
"""

import sqlite3
import copy


class FdWrite:
    def __init__(self, db_address):
        self.db_address = db_address

    def __check_df_format(self, df, names):
        """check set of df indecies and column names are euqal to set of names
        except if incorrect

        Params:
        df: pandas.DataFrame
        names: list or set of df names

        Return:
        None

        Notes:
        None
        """
        # check df in correct format
        if set(list(df.index.names) + list(df.columns)) != set(names):
            raise Exception("Incorrect DF format (check row and index labels)")

    def __insert_df(self, recordsDF, tableName):
        """Insert zero or more records from pandas df into specified table

        Params:
        records: pandas.DataFrame of rows corresponding to records in table
        named tableName and indexed by the primary key's

        Return:
        none

        Notes:
        -If fuplicate PK in db, quietly update
        -Will throw exception if given empty dataframe
        """
        # TODO: Potentially remove this; might be expensive
        recordsDF = copy.deepcopy(recordsDF)
        conn = sqlite3.connect(self.db_address)
        # one of SQLites wierder idiosyncracies, pragmas must be executed
        # for each connection
        conn.execute("PRAGMA foreign_keys = ON;")
        old_index = recordsDF.index
        recordsDF.reset_index(inplace=True)
        # construct table fields so order independant
        row_pos = "(" + ",".join(recordsDF.columns) + ")"
        # construct rest of query
        query = "INSERT OR REPLACE INTO " + tableName + row_pos + " \n VALUES \n"
        row_params = "(" + ",".join(recordsDF.shape[1] * ["?"]) + ")"
        query += (",".join(recordsDF.shape[0] * [row_params])) + ";"
        # create parameters list
        params = [y for x in recordsDF.values.tolist() for y in x]
        recordsDF.set_index(old_index, inplace=True)
        conn.cursor().execute(query, params)
        conn.commit()
        conn.close()

    def t_insert_df(self, recordsDF, tableName):
        """Method to aid with unit testing, ignore this
        """
        self.__insert_df(recordsDF, tableName)

    def t_check_df_format(self, df, names):
        """Method to aid with unittesting, ignore this
        """
        self.__check_df_format(df, names)

    def write_asset_classes(self, asset_classes):
        """Add zero or more records of asset classes to fin database

        Params:
        asset_classes: pandas.DataFrame of format:
        {Columns: [], Index: [AssetClassName<String>]}
        | pandas dataframe containing records of asset classes to be
          stored in database

        Return:
        None

        Notes:
        - If given non unique PK, quietly update record
        - Will throw exception if given empty dataframe
        """
        self.__check_df_format(asset_classes, ["AssetClassName"])
        self.__insert_df(asset_classes, "AssetClass")

    def write_assets(self, assets):
        """Add zero or more records of assets to fin database

        Params:
        asset_classes: pandas.DataFrame of format:
        {Columns: [Name<String>, AssetClassName<String>],
         Index: [AssetTicker<String>]}
        | pandas dataframe containing records of assets to be
          stored in database

        Return:
        None

        Notes:
        - If given non unique PK, quietly update record
        - If one or more records contain reference to AssetClassName not in
          AssetClass(AssetClassName), raise exception
        """
        self.__check_df_format(assets, ["Name", "AssetClassName", "AssetTicker"])
        self.__insert_df(assets, "Asset")

    def write_asset_values(self, values):
        """Add zero or more records of values to fin database

        Params:
        assets: Pandas dataframe of format
        {Columns: [AOpen<Decimal.decimal>, AClose<Decimal.decimal>,
                AHigh<Decimal.decimal>, ALow<Decimal.decimal>]
         Index: [AssetTicker<String>, ADate <datetime.date>]}

        Return:
        None

        Notes:
        - If given non unique PK, quietly update record
        - If one or more records contain reference to AssetTicker not in
            Asset(AssetTicker), raise exception
        - If data added to database would create holes, raise exception
        - Will throw exception if given empty dataframe
        """
        # check df in right format
        self.__check_df_format(
            values,
            [
                "AOpen",
                "AClose",
                "AHigh",
                "ALow",
                "ADate",
                "AssetTicker",
                "IsInterpolated",
            ],
        )
        # fix date and decimal types
        values["AOpen"] = values["AOpen"].map(str)
        values["AClose"] = values["AClose"].map(str)
        values["AHigh"] = values["AHigh"].map(str)
        values["ALow"] = values["ALow"].map(str)
        values.reset_index(inplace=True)
        values["ADate"] = values["ADate"].map(str)
        values.set_index(["AssetTicker", "ADate"], inplace=True)
        self.__insert_df(values, "AssetValue")

    def write_dividend_payouts(self, payouts):
        """Add zero or more records of divident payouts to fin database

        Params:
        asset_classes: pandas.DataFrame of format:
        {Columns: [Payout<decima.Decimal>]
                   Index: [AssetTicker<String>, PDate<datetime.date>]}
        | pandas dataframe containing records of payouts to be
          stored in database

        Return:
        None

        Notes:
        - If given non unique PK, quietly update record
        - If one or more records contain reference to AssetTicker not in
          Asset(AssetTicker), raise exception
        - Will throw exception if given empty dataframe
        """
        self.__check_df_format(payouts, ["PDate", "Payout", "AssetTicker"])
        payouts.reset_index(inplace=True)
        payouts["PDate"] = payouts["PDate"].map(str)
        payouts["Payout"] = payouts["Payout"].map(str)
        payouts.set_index(["AssetTicker", "PDate"], inplace=True)
        self.__insert_df(payouts, "DividendPayout")
