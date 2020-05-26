"""
Helper methods for finda testing
"""


import pandas as pd

from Finda import FdMultiController

# these are the database names used for testing, and should therefore not
# be populated
TESTINGDBS = ["__seeded_test_db__", "testDB1", "__empty_test_db__", "RaNdOmGibBeRiSh"]


def compare_df(dfT, dfR):
    """
    Compare dataframe values, columns and indecies regardless of column and index
    order
    """
    dfT = dfT.reindex(sorted(dfT.columns), axis=1)
    dfR = dfR.reindex(sorted(dfR.columns), axis=1)
    dfR = dfR.sort_index()
    dfT = dfT.sort_index()
    # assert (list(dfT.dtypes) == list(dfR.dtypes))
    assert pd.DataFrame.equals(
        dfR.sort_index(), dfT.sort_index()
    ), "dataframe mismatch in \
                                                   calling function"


def clear_DBs():
    # remove all financial database whos names used for testing environment
    for ndb in TESTINGDBS:
        FdMultiController.fd_remove(ndb)
