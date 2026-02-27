import pandas as pd
import logging
import time
import random

from src.config.keywords import FINTECH_KEYWORDS
from src.config.countries import COUNTRIES
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
        # EXTRACT
        logging.info("Extracting data from Google Trends...")

        all_data = []

        for country_code in COUNTRIES.keys():
            for keyword in FINTECH_KEYWORDS:

                logging.info(f"Fetching {keyword} - {country_code}")

                try:
                    df = fetch_trends_data(keyword, country_code)

                    if not df.empty:
                        all_data.append(df)

                    # evitar rate limiting
                    time.sleep(random.uniform(5, 9))

                except Exception as e:
                    logging.error(f"Error fetching {keyword}-{country_code}: {e}")

        if not all_data:
            logging.warning("No data extracted. Pipeline stopped.")
            return

        raw_df = pd.concat(all_data, ignore_index=True)

        # Guardar raw backup
        raw_df.to_csv(RAW_PATH, index=False)
        logging.info(f"Raw data saved to {RAW_PATH}")

        # TRANSFORM   
        logging.info("Transforming data...")

        clean_df = transform_pipeline(raw_df)

        if clean_df.empty:
            logging.warning("No data after transformation. Pipeline stopped.")
            return

        # Guardar processed backup
        clean_df.to_csv(PROCESSED_PATH, index=False)
        logging.info(f"Processed data saved to {PROCESSED_PATH}")

        # LOAD
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
    