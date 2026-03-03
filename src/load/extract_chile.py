
import pandas as pd
import logging
import time
import random
import sys
from pathlib import Path

# Agregar raíz del proyecto al path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.config.keywords import FINTECH_KEYWORDS
from src.extract.google_trends import fetch_trends_data
from src.transform.clean_transform import transform_pipeline
from src.load.supabase_loader import upload_dataframe

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

def extract_chile_only():

    
    setup_logging()
    print("🇨🇱 EXTRACCIÓN INCREMENTAL: SOLO CHILE")
    
    country_code = "CL"  # Solo Chile
    all_data = []
    
    print(f" Extrayendo {len(FINTECH_KEYWORDS)} keywords para Chile...")
    print()
    
    for i, keyword in enumerate(FINTECH_KEYWORDS, 1):
        logging.info(f"[{i}/{len(FINTECH_KEYWORDS)}] Fetching: {keyword} - {country_code}")
        
        try:
            # Extraer datos de Google Trends
            df = fetch_trends_data(keyword, country_code)
            
            if not df.empty:
                all_data.append(df)
                logging.info(f"   {len(df)} registros obtenidos")
            else:
                logging.warning(f"   No data for {keyword}")
            
            # rate limiting
            wait_time = random.uniform(12, 20)
            logging.info(f"    Waiting {wait_time:.1f}s before next request...")
            time.sleep(wait_time)
            
        except Exception as e:
            logging.error(f"    Error: {e}")
            continue

    if not all_data:
        logging.error(" No data extracted for Chile. Aborting.")
        return
    
    raw_df_chile = pd.concat(all_data, ignore_index=True)
    logging.info(f" Total raw records extracted: {len(raw_df_chile)}")
    
    # Guardar backup raw de Chile
    chile_raw_path = project_root / "data" / "raw" / "google_trends_chile_raw.csv"
    raw_df_chile.to_csv(chile_raw_path, index=False)
    logging.info(f" Chile raw data saved to: {chile_raw_path}")
    
    print()
    print(" Transforming data...")
    
  
    clean_df_chile = transform_pipeline(raw_df_chile)
    
    if clean_df_chile.empty:
        logging.warning(" No data after transformation. Pipeline stopped.")
        return
    
    logging.info(f" Clean records after transformation: {len(clean_df_chile)}")
    
    # Guardar backup clean de Chile
    chile_clean_path = project_root / "data" / "processed" / "google_trends_chile_clean.csv"
    clean_df_chile.to_csv(chile_clean_path, index=False)
    logging.info(f" Chile clean data saved to: {chile_clean_path}")
    
    print()
    print("📤 Uploading to Supabase...")
    print("    Using UPSERT (won't duplicate existing data)")
    print()
    
    # Subir a Supabase (usa upsert, no duplica)
    upload_dataframe(clean_df_chile)
    
    print()
    print("✅ CHILE DATA EXTRACTION COMPLETED")
    print("Summary:")
    print(f"   Raw records extracted: {len(raw_df_chile)}")
    print(f"   Clean records: {len(clean_df_chile)}")
    print(f"   Uploaded to Supabase")

if __name__ == "__main__":
    extract_chile_only()

