import pandas_datareader as pdread
import pandas as pd
import os
from .api_class import ApiObject as apic
from .data_harvester import DataHarvester as dhav
from .initialization import Initializer as int_constructor


def run_me():

    path = os.path.dirname(__file__)
    path = os.path.dirname(path)

    path = os.path.join(path, "apis_access")

    api_calls_api1 = 50
    api_calls_api2 = 50
    api1 = apic(
        "yfinance", ["bonds", "comodities_future", "index_funds","stocks"], api_calls_api1
    )
    api2 = apic("nomics", ["crypto", "currency"], api_calls_api2, path, True)

    dh = dhav([api1, api2])

    dh.start_updating()


if __name__ == "__main__":
    run_me()
