import logging
import pandas as pd
from datetime import datetime

"""
    Made in a separate class because
    I was thinking on having 2 types of logging.
    Detailed one and a less detailed one that is easier
    to follow.
"""


class Logger:
    def __init__(self):
        logging.basicConfig(filename="dh.log", level=logging.INFO)

    def log_simple(self, message):
        logging.info(message)

    def log_api_call(self, asset_class, ticker, start_date, end_date):
        logging.info(
            "calling for:\nasset_class: "
            + asset_class
            + " ticker: "
            + ticker
            + " start_date : "
            + start_date
            + " end_date: "
            + end_date
        )

    def crit(self, asset_class, ticker, start_date, end_date):
        logging.critical(
            "WRONG DATAFRAME FORMAT FROM API CALL at " + str(datetime.now())
            + "\nOR WRONG TICKER NAME"
        )
        logging.critical(
            "calling for:\nasset_class: "
            + asset_class
            + " ticker: "
            + ticker
            + " start_date : "
            + start_date
            + " end_date: "
            + end_date
        )

    def error_log(self, message):
        logging.error(message)
