import pandas as pd
import os
from constants import Timeframe
from typing import Literal

def get_df(pair: str, timeframe: Timeframe, path_append: str ="", file_type: Literal['PKL', 'CSV', 'PARQUET'] = 'PKL') -> pd.DataFrame:
    ext = file_type.lower()
    source_dir = path_append + f"./src/data/{ ext }/"
    print(pair)

    for file in os.scandir(source_dir):
        if pair in file.path and timeframe.name in file.path:
            match file_type:
                case 'PKL':
                    return pd.read_pickle(file.path)
                case 'CSV':
                    return pd.read_csv(file.path)
                case 'PARQUET':
                    return pd.read_parquet(file.path)
            
    raise FileNotFoundError("Could not find pkl file: {pair}-{timeframe.name}")

def save_df(df: pd.DataFrame, file_name: str, file_type: Literal['PKL', 'CSV', 'PARQUET'] = 'PKL'):
    ext = file_type.lower()
    dest_dir = f"./src/data/{ ext }/"

    if not os.path.exists(dest_dir):
        print("making dir")
        os.mkdir(dest_dir)

    match file_type:
        case 'PKL':
            df.to_pickle(f"{ dest_dir }{ file_name }.pkl")
        case 'CSV':
            df.to_csv(f"{ dest_dir }{ file_name }.csv")
        case 'PARQUET':
            df.to_parquet(f"{ dest_dir }{ file_name }.parquet")
            
    