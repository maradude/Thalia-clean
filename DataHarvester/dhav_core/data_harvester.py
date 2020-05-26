import pandas_datareader as pdread
import pandas as pd
import nomics
import os
from datetime import datetime, timedelta
import sys
from .logger_class import Logger


# find a better way to reach Finda
sys.path.append("../../../")
from Finda import FdMultiController


class DataHarvester:
    def __init__(self, api_list,test=False):
        self.api_list = api_list
        self.testing = test
        if not self.testing:
            FdMultiController.fd_register("asset")
            self.conn = FdMultiController.fd_connect("asset", "rw")

        self.log = Logger()

    """
        Makes the api call based on the asset_class and ticker given.
        Also need a start and end date.

        date format: "YYYY-MM-DD"

        If the start date is older than the oldest available date
        then the oldest available date is returned. 
    """

    def get_data(self, asset_class, ticker, start_date, end_date):

        for api in self.api_list:
            if asset_class in api.supported_assets:

                self.log.log_api_call(asset_class, ticker, start_date, end_date)
                df = api.call_api(asset_class, ticker, start_date, end_date)
                self.log.log_simple("api returned " + str(type(df)))
                return df

    """
        Returns the current index of a api from the persitant data.
        The ticker under the index has not been updated yet.
    """

    def current_index(self, api):
        path = os.path.dirname(__file__)
        path = os.path.dirname(path)
        path = os.path.join(path, "persistent_data/" + api.name + "_position.csv")
        position_frame = pd.read_csv(path)

        return position_frame["Position Universal"][0]

    def next_index(self, api):
        """
            Moves the update index by 1
            If it reaches the end of the list starts again from the first position
        """

        path = os.path.dirname(__file__)
        path = os.path.dirname(path)
        path = os.path.join(path, "persistent_data/" + api.name + "_position.csv")
        position_frame = pd.read_csv(path)

        path = os.path.dirname(path)
        path = os.path.join(path, "update_list_" + api.name + ".csv")

        update_list = pd.read_csv(path)

        # get number of tickers to update
        number_rows = update_list.shape[0]

        index_position = position_frame["Position Universal"][0]
        index_position += 1

        # if the end of the list is reached reset
        if index_position + 1 > number_rows:
            index_position = 0

        position_frame["Position Universal"][0] = index_position

        path = os.path.dirname(__file__)
        path = os.path.dirname(path)
        path = os.path.join(path, "persistent_data/" + api.name + "_position.csv")
        # write back to persistent data folder
        position_frame.to_csv(path, index=False)
        return 0

    def update_on_index(self, api):
        """
            Updates the ticker under the index.
            Ignores API calls that do not work because the ticker does not exist.
        """

        path = os.path.dirname(__file__)
        path = os.path.dirname(path)

        # get update list and index position to know the name of the ticker to update
        path = os.path.join(path, "persistent_data/update_list_" + api.name + ".csv")
        up_list = pd.read_csv(path)
        index = self.current_index(api)

        ticker_under_index = up_list.iloc[index]
        ticker_name = up_list.iloc[index]["Ticker"]

        start_date = ""
        # set end_date to yesterday
        end_date = datetime.date(datetime.now()) + timedelta(days=-1)

        end_date = end_date.strftime("%Y-%m-%d")

        # if end_date and Last Update are the same day it means that
        # a full circle has been done and updating can stop for this api
        if end_date == ticker_under_index["Last_Update"]:
            self.log.log_simple("Updated all tickers for today for with current API")
            return "full_circle"
        # for first update there is no date written in the update list so the ticker has NaN value
        if pd.isna(ticker_under_index["Last_Update"]):
            start_date = "1970-1-1"
        else:
            # get the date from the list
            start_date = ticker_under_index["Last_Update"]
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            # add 1 more day so that the last date is not called twice
            start_date = start_date + timedelta(days=1)
            start_date = str(start_date)

        # if data retrieval fails just go to the next ticker
        # in this call to get_date we can see that standard format for calling data from APIs
        # this might get changed when implementing dividents
        data_set_retrieved = self.get_data(
            ticker_under_index["Asset_Class"],
            ticker_under_index["Ticker"],
            start_date,
            end_date,
        )

        # the api format returns 1 in case of no data from the API call
        # if the df received is not int it means it is a dataframe and the call
        # worked.
        
        if type(data_set_retrieved) != int:
            start_date = data_set_retrieved["ADate"][0]
            self.log.log_simple(
                "Received data frame with data between "
                + str(start_date)
                + " - "
                + str(end_date)
            )

            
            self.write_to_db(data_set_retrieved, ticker_name)
            self.write_to_up_list(api, start_date, end_date)
            return 0
        else:
            return 1

    def write_to_up_list(self, api, start_date, end_date):

        """
            Writes back in the persitant data update list.
            This is done after updating a ticker.
            At this moment the data in update list should corespond with the
            data in the database.
        """
        path = os.path.dirname(__file__)
        path = os.path.dirname(path)

        path = os.path.join(path, "persistent_data/update_list_" + api.name + ".csv")

        up_list = pd.read_csv(path)
        index = self.current_index(api)
        up_list.loc[index, "Last_Update"] = end_date
        if pd.isna(up_list.loc[index, "Earliest_Record"]):
            up_list.loc[index, "Earliest_Record"] = start_date

        up_list.to_csv(path, index=False)

    def start_updating(self):
        """
        Start the updating process.
        Each API does as many calls as there are in the calls_per_run
        variable in the api wrapper.
        """
        self.log.log_simple("\n\nStarted update at: " + str(datetime.now()))

        for api in self.api_list:

            self.log.log_simple(
                "Started updating " + api.name + " at " + str(datetime.now())
            )

            self.log.log_simple(
                "Updating for "
                + api.name
                + " doing "
                + str(api.api_calls_per_run)
                + " calls"
            )

            for x in range(api.api_calls_per_run):
                answer = self.update_on_index(api)
                if answer == 0:
                    self.next_index(api)
                elif answer == 1:
                    self.next_index(api)
                # can change it to 2 but I need a good reason too
                elif answer == "full_circle":
                    break
            self.log.log_simple(
                "Finished updating " + api.name + " at " + str(datetime.now())
            )
        self.log.log_simple("Finished all  updates at: " + str(datetime.now()))

    def add_interpolation_to_df(self, df):
        """
            Interpolation 
        """
        interpolated_df = pd.DataFrame(columns=df.columns)

        interpolated_df.reset_index()
        # if only 1 row
        if df.shape[0] == 1:
            return df
        else:
            for index_rows in range(df.shape[0] - 1):

                today = df["ADate"][index_rows]

                tomorrow = df["ADate"][index_rows + 1]

                delta = tomorrow - today

                rows_interpolated = []
                
                df_today = df.loc[index_rows]
                df_today_app = df_today.to_frame().transpose()

                interpolated_df = interpolated_df.append(
                    df_today_app, ignore_index=True, sort=False
                )

                if delta.days > 1:

                    for index_days in range(delta.days - 1):

                        interpolated_row = df_today.copy()

                        interpolated_row["ADate"] = today + timedelta(
                            days=index_days + 1
                        )

                        interpolated_row["IsInterpolated"] = 1

                        interpolated_row = interpolated_row.to_frame().transpose()

                        rows_interpolated.append(interpolated_row)

                    df_rows = pd.concat(rows_interpolated, ignore_index=True, sort=True)

                    interpolated_df = interpolated_df.append(
                        df_rows, ignore_index=True, sort=False
                    )

            # add the last row to the dataframe
            df_today = df.loc[index_rows+1]
            df_today_app = df_today.to_frame().transpose()
            interpolated_df = interpolated_df.append(
                    df_today_app, ignore_index=True, sort=False
                )

            
            return interpolated_df

    """
        {Columns: [AOpen<Decimal.decimal>, AClose<Decimal.decimal>, 
            AHigh<Decimal.decimal>, ALow<Decimal.decimal>, IsInterpolated<Integer>] 
            Index: [AssetTicker<String>, ADate <datetime.date>]}
    """

    def write_to_db(self, dataset_to_sql, ticker_name):
       
        self.log.log_simple(
            "Start interpolation" + "dataframe shape: " + str(dataset_to_sql.shape)
        )

        df_to_send = self.add_interpolation_to_df(dataset_to_sql)
        self.log.log_simple(
            "Data Frame Interpolated" + "dataframe shape: " + str(df_to_send.shape)
        )
        df_to_send = df_to_send.set_index(["AssetTicker", "ADate"])

        self.log.log_simple("Writing interpolted dataframe to DB")
        
        if not self.testing:
            self.conn.write.write_asset_values(df_to_send)
