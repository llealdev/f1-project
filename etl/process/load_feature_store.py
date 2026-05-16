import os 
import dotenv 
import pandas as pd 
import psycopg2
from sqlalchemy import create_engine 

dotenv.load_dotenv()

def load_feature_store_db(df: pd.DataFrame, uri_db: str): 
    
    if df.empty:
        print("Nenhnum dado econtrado")
        return
    
    engine = create_engine(uri_db)

    df.to_sql(name='fs_f1_all', con=engine, if_exists="append", index=False)    

def main(): 
    URI_DB = os.getenv("DB_FETURE_STORE")

    df = pd.read_csv("data/abt_f1_drivers_champions.csv", sep=";")

    load_feature_store_db(df, URI_DB)

    print("Load com sucesso")

if __name__ == '__main__':
    main()