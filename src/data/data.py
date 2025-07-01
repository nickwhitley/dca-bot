import pandas
import os

def save_df_to_pkl(df, file_name):
    #need to check if dir exists
    path = "./src/data/pkl/"
    df.to_pickle(f"{ path }{ file_name }.pkl")

def save_df_to_csv(df, file_name):
    path = "./src/data/csv/"
    if os.path.exists(path):
        df.to_csv(f"{ path }{ file_name }.csv")
    else:
        os.mkdir(path)
        df.to_csv(f"{ path }{ file_name }.csv")