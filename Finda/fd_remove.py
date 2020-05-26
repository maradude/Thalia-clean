import sqlite3


class FdRemove:
    def __init__(self, db_address):
        self.db_address = db_address

    def deleteValues(self, ticker, date):
        date = str(date)
        "--Only need ticker + day columns"
        conn = sqlite3.connect(self.db_address)
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM AssetValue WHERE AssetTicker =? AND ADate=?", (ticker, date)
        )
        conn.commit()
        conn.close()

    def delete_div_payouts(self, ticker):
        """Delete all divident payouts with assetTicker ticker
        """
        conn = sqlite3.connect(self.db_address)
        cur = conn.cursor()
        cur.execute("PRAGMA foreign_keys = ON")
        cur.execute("DELETE FROM DividendPayout WHERE AssetTicker =? ", (ticker,))
        conn.commit()
        conn.close()

    def deleteAssets(self, ticker):
        """
        --Only need asset tickers
        will delete associated values
        """
        conn = sqlite3.connect(self.db_address)
        cur = conn.cursor()
        cur.execute("PRAGMA foreign_keys = ON")
        cur.execute("DELETE FROM Asset WHERE AssetTicker =? ", (ticker,))
        conn.commit()
        conn.close()

    def deleteAssetClasses(self, assetclassname):
        """
        -- only asset
        will delete associated assets and values
        """
        conn = sqlite3.connect(self.db_address)
        cur = conn.cursor()
        cur.execute("PRAGMA foreign_keys = ON")
        cur.execute(
            "DELETE FROM AssetClass WHERE AssetClassName =? ", (assetclassname,)
        )
        conn.commit()
        conn.close()


"""
fdr = fdremove('finData4.db')
#fdr.deleteValues(df0, 'ASS13', '2020-02-01')
#fdr.deleteAssets(df1, 'RCK')
fdr.deleteAssetClasses(df2, 'PETROLIUM DERIVATIVE')

print(df1)
print(df0)
print(df2)
"""
