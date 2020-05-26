import pandas_datareader as pdread
import pandas as pd
from datetime import datetime
import nomics as nc
import os
import numpy as np
from .logger_class import Logger



class ApiObject:
    def __init__(
        self, name, supported_assets, api_calls_per_run, path="", has_key=False
    ):

        self.name = name
        self.has_key = has_key
        self.supported_assets = supported_assets
        if self.has_key == True:
            path = os.path.join(path, name)
            with open(path,"r") as f:
                self.key = f.read().rstrip()
        else:
            self.key = False
        
        self.api_calls_per_run = api_calls_per_run
        self.log = Logger() 

    def yahoo_finance(self, asset_class, ticker, start_date, end_date):
        """
            Call yfinance trough pandas datareader
        """
        
        try:
            pass
            dataframe_retrieved = pdread.DataReader(
                ticker, start=start_date, end=end_date, data_source="yahoo"
            )
            
        except (pdread._utils.RemoteDataError,KeyError) as err:
            self.log.error_log(err)
            return 1  # return 1 if fail to get dataframe

       
        return self.yahoo_df_format(dataframe_retrieved,ticker)

    

    def yahoo_df_format(self,df,ticker ):
        """
        function that formats the dataframe received from yfinance to 
        a format used by Finda 
        """

        #to modify the index column we first need to reset the index
        df.reset_index(level=0, inplace=True)
        
        # change Date column to datetime.date
        df["Date"] = pd.to_datetime(
                df["Date"]
            ).apply(lambda x: x.date())

        # rename columns
        df = df.rename(columns={"Date":"ADate","Adj Close":"AClose","Low":"ALow","High":"AHigh","Open":"AOpen"})
        #add AssetTicker and Interpolated
        df["AssetTicker"] = ticker
        df["IsInterpolated"] = 0


        #remove unused columns
        df = df.drop(columns=["Volume","Close"])
       
        return df

    


    def nomics_format(self,df,ticker):
        
        """
            Format dataframe from nomics to fit Finda format.
        """
        
        
        df = pd.DataFrame.from_dict(df)
        df = df.rename(
            columns={
                "timestamp": "ADate",
                "rate": "AClose",
            }  
        )

        df["ADate"] = [
            datetime.strptime(word.split("T")[0], "%Y-%m-%d").date()
            for word in df["ADate"]
        ]
        df["AHigh"] = np.nan
        df["ALow"] = np.nan
        df["AOpen"] = np.nan
        df["AssetTicker"] = ticker
        df["IsInterpolated"] = 0
        df["AClose"] = pd.to_numeric(df["AClose"])
        
        return df

    def nomics_call(self, asset_class, ticker, start_date, end_date):
        
        nomics_api = nc.Nomics(self.key)

        currency = nomics_api.ExchangeRates.get_history(
            currency=ticker,
            start=start_date + "T00:00:00Z",
            end=end_date + "T00:00:00Z",
        )

        #nomics returns a empty list when there is no data 
        if(len(currency) == 0):
            return 1


        return self.nomics_format(currency,ticker)

    """
        This check_df_format should be the same with Finda or whatever db
        format is required
    """

    def check_df_format(self,df):
        if(not isinstance(df,int)):

            if(set(df.columns.values) != set(['ADate', 'AHigh', 'ALow', 'AOpen', 'AClose', 'AssetTicker',
        'IsInterpolated']) ):
                return False
            if( not type(df["ADate"][0] is datetime.date )): 
                self.log.log_simple("ADate Wrong format")
                return False
            if (not type(df["AHigh"][0]) is np.float64):
                self.log.log_simple("AHigh Wrong format")
                return False
            if(not type(df["ALow"][0]) is np.float64 ):
                self.log.log_simple("ALow Wrong format")
                return False
            if(not type(df["AOpen"][0]) is np.float64 ):
                self.log.log_simple("AOpen Wrong format")
                return False
            if(not type(df["AClose"][0]) is np.float64):
                self.log.log_simple("AClose Wrong format")
                return False
            if(not type(df["AssetTicker"][0]) is str):
                self.log.log_simple("AssetTicker Wrong format")
                return False
            if(not type(df["IsInterpolated"][0]) is np.int64 ):
                self.log.log_simple("IsInterpolated Wrong format")
                return False

            return True
        else:
            return False

    def call_api(self, asset_class, ticker, start_date, end_date):
        if self.name == "yfinance":
            df = self.yahoo_finance(asset_class, ticker, start_date, end_date) 
            formated =  self.check_df_format(df)
            if formated == False:
                self.log.crit(asset_class,ticker,start_date,end_date)
            
            return df

        elif self.name == "nomics":
            df = self.nomics_call(asset_class, ticker, start_date, end_date)
            formated =  self.check_df_format(df)
            if formated == False:
                self.log.crit(asset_class,ticker,start_date,end_date)
           
            return df
