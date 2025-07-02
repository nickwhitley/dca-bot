import pandas as pd
import os

def save_df_to_pkl(df, file_name):
    path = "./src/data/pkl/"
    if not os.path.exists(path):
        os.mkdir(path)
    df.to_pickle(f"{ path }{ file_name }.pkl")

def get_df_from_pkl(pair, timeframe):
    directory = "./src/data/pkl/"
    for file in os.scandir(directory):
        if pair in file.path and str(int(timeframe / 60)) in file.path:
            print(file.path)

def save_df_to_csv(df, file_name):
    path = "./src/data/csv/"
    if not os.path.exists(path):
        os.mkdir(path)
    df.to_csv(f"{ path }{ file_name }.csv")