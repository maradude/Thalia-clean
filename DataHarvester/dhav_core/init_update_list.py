"""
    Script for reseting the persitant_data 
"""


from .initialization import Initializer as int_constructor
from .api_class import ApiObject as apic


def reset_update_lists():

    api1 = apic("yfinance", ["bonds", "comodities_future", "index_funds","stocks"], 10)
    api2 = apic("nomics", ["crypto", "currency"], 0, True)

    initer = int_constructor([api1, api2])
    initer.construct_update_list()
    initer.construct_position()


if __name__ == "__main__":
    reset_update_lists()
