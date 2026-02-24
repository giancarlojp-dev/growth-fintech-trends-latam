import pandas as pd
import os
import logging

from src.extract.google_trends import fetch_trends_data
from src.transform.clean_transform import transform_pipeline
from src.config.settings import RAW_PATH, PROCESSED_PATH
from src.load.supabase_loader import upload_dataframe


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

def run_pipeline(load_to_db: bool = True):

    logging.info("Starting ETL pipeline...")
    
    try:
        # Extract 
        logging.info("Extracting data from Google Trends...")
        raw_df = fetch_trends_data()

        if raw_df.empty: 
            logging.warning("No data extracted. Pipeline stopped")
            return

        #Guardar raw
        raw_df.to_csv(RAW_PATH, index=False)
        logging.info(f"Raw data saved to {RAW_PATH}")

        #Transform
        logging.info("Transforming data...")
        clean_df = transform_pipeline(raw_df)

        if clean_df.empty: 
            logging.warning("No data after transformation. Pipeline stopped.")
            return 

        #Guardar processed
        clean_df.to_csv(PROCESSED_PATH, index=False)

        #Load
        if load_to_db:
            logging.info("Loading data to Supabase...")
            upload_dataframe(clean_df)
            logging.info("Upload completed")

        logging.info("Pipeline completed successfully")

    except Exception as e:
        logging.error(f"Pipeline failed: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    setup_logging()
    run_pipeline()

