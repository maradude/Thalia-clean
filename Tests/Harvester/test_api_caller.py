import pytest
import os
import sys
'''
    This test has been made in order to verify that the integration with 
    CircleCI is done.
'''
sys.path.append('../..')

from DataHarvester.dhav_core.data_harvester import DataHarvester as dhorda
from DataHarvester.dhav_core.initialization import Initializer as preulde_dhorda
from DataHarvester.dhav_core.api_class import ApiObject as dhorda_api_warper


'''
    Test the creation of a api.
    This includes creating a file that simulates a key in order
    to have 100% test coverage.
    keys are stored in a file with the name of the api

    The api wrapper is highly dependant on the situation
    Not many restrictions apply. Just store data and check if 
    it is retrieved correctly.
'''

def create_fictional_key(api_name,key_to_write,path):
    file = open(path+api_name,"w")
    file.write(key_to_write)
    file.close()

def remove_fictional_key(path,name):
    os.remove(path+name)

def test_api_wraper_creation():
    name = "test_api"
    supported_assets = ['milk','lean_hogs','tanks']
    api_calls_round = 90
    has_key = True
    key_to_write = "123khljlkjlkj"
    
    path_apis_acces =  os.path.abspath(__file__)
    
    path_apis_acces = os.path.dirname(path_apis_acces)
    path_apis_acces = os.path.dirname(path_apis_acces)
    path_apis_acces = os.path.dirname(path_apis_acces)

    path_apis_acces = os.path.join(path_apis_acces,'DataHarvester/apis_access/')
    

    create_fictional_key(name, key_to_write,path_apis_acces)
    api_caller = dhorda_api_warper(name, supported_assets, api_calls_round, path_apis_acces,has_key)

    assert api_caller.name == name
    assert api_caller.supported_assets == supported_assets
    assert api_caller.api_calls_per_run == api_calls_round
    assert api_caller.has_key == has_key
    assert api_caller.key == key_to_write
    remove_fictional_key(path_apis_acces,name)
