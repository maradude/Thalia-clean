import sys
import os
import pandas as pd
sys.path.append('../..')

from DataHarvester.dhav_core.data_harvester import DataHarvester as dhorda

current_dir = os.path.dirname(__file__)

def test_interpolation():
    to_int = os.path.join(current_dir,"to_interpolate.csv")
    df_to_test = pd.read_csv(to_int,float_precision=None)
    df_to_test["ADate"] = [
            word.split("T")[0]
            for word in df_to_test["ADate"]
        ]

    df_to_test['ADate'] = df_to_test['ADate'].astype('datetime64[ns]')
    
    result = os.path.join(current_dir, "interpolation_result.csv")
    df_correct = pd.read_csv(result,index_col=0)
    testing = True
    dh = dhorda([],testing)

    df_to_test["AHigh"] = pd.to_numeric(df_to_test["AHigh"])
    df_to_test["ALow"] = pd.to_numeric(df_to_test["ALow"])
    df_to_test["AOpen"] = pd.to_numeric(df_to_test["AOpen"])
    df_to_test["AClose"] = pd.to_numeric(df_to_test["AClose"])


    calculated_df = dh.add_interpolation_to_df(df_to_test)
    
    calculated_df = calculated_df.drop(columns="Unnamed: 0")
   
    calculated_df["ADate"] =  [time.date() for time in calculated_df['ADate']] 
    df_correct["ADate"] =  pd.to_datetime(df_correct["ADate"])
    for x in df_correct.columns:
        calculated_df[x]=calculated_df[x].astype(df_correct[x].dtypes.name)
    

    assert df_correct["ALow"].equals(calculated_df["ALow"])
    assert df_correct["AHigh"].equals(calculated_df["AHigh"])
    assert df_correct["AOpen"].equals(calculated_df["AOpen"])
    assert df_correct["AClose"].equals(calculated_df["AClose"])
    assert df_correct["AssetTicker"].equals(calculated_df["AssetTicker"])
    assert df_correct["IsInterpolated"].equals(calculated_df["IsInterpolated"])
    assert df_correct["ADate"].equals(calculated_df["ADate"])
   
    