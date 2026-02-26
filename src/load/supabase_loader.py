import os
import logging
import pandas as pd
from supabase import create_client, Client
from dotenv import load_dotenv 

load_dotenv()  
logging.basicConfig(level=logging.INFO)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")


def get_supabase_client() -> Client:
    """ Create Supabase client instance. """
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Supabase credentials not set in environment variables.")

    return create_client(SUPABASE_URL, SUPABASE_KEY)


def upload_dataframe(df: pd.DataFrame, table_name: str = "fintech_trends"):
    """ Upload pandas dataframe to Supabase table. """

    if df.empty:
        logging.warning("Attempted to upload empty dataframe.")
        return

    client = get_supabase_client()
    records = df.to_dict(orient="records")

    try:
        response = client.table(table_name).insert(records).execute()

        if response.data:
            logging.info(f"Inserted {len(response.data)} rows into {table_name}")
        else:
            logging.warning("Insert completed but no data returned.")

    except Exception as e:
        logging.error(f"Upload failed: {str(e)}")
        raise

def test_connection():
    """Test Supabase connection"""
    try:
        client = get_supabase_client()
        print(" Supabase connection successful!")
        print(f"   URL: {SUPABASE_URL}")
        return True
    except Exception as e:
        print(f" Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()

