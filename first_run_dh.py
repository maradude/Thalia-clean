from DataHarvester.dhav_core.run_updates import run_me
from DataHarvester.dhav_core.init_update_list import reset_update_lists
from DataHarvester.dhav_core.init_finda_db_structure import init_db_finda
import os



current_path = os.path.abspath(__file__)
current_path = os.path.dirname(current_path)
path_persistent_data = os.path.join(current_path,"DataHarvester/persistent_data")

if not os.path.exists(path_persistent_data):
    os.makedirs(path_persistent_data)

reset_update_lists()
init_db_finda()

