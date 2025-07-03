import pandas as pd
import os
from constants import Timeframe

def save_df_to_pkl(df: pd.DataFrame, file_name: str):
    dest_dir = "./src/data/pkl/"
    if not os.path.exists(dest_dir):
        os.mkdir(dest_dir)
    df.to_pickle(f"{ dest_dir }{ file_name }.pkl")

def get_df_from_pkl(pair: str, timeframe: Timeframe, path_append: str ="") -> pd.DataFrame:
    source_dir = path_append + "./src/data/pkl/"
    for file in os.scandir(source_dir):
        if pair in file.path and timeframe.name in file.path:
            return pd.read_pickle(file.path).copy
    raise FileNotFoundError("Could not find pkl file: {pair}-{timeframe.name}")

def save_df_to_csv(df: pd.DataFrame, file_name: str):
    path = "./src/data/csv/"
    if not os.path.exists(path):
        os.mkdir(path)
    df.to_csv(f"{ path }{ file_name }.csv")