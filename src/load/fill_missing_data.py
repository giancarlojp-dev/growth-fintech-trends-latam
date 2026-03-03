import pandas as pd
import logging
import time
import random
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.config.keywords import FINTECH_KEYWORDS
from src.config.countries import COUNTRIES
from src.extract.google_trends import fetch_trends_data
from src.transform.clean_transform import transform_pipeline
from src.load.supabase_loader import get_supabase_client, upload_dataframe

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

def get_existing_combinations():
    
    client = get_supabase_client()
 
    response = client.table("fintech_trends")\
        .select("country_code, keyword")\
        .execute()
    
    df = pd.DataFrame(response.data)

    existing = set()
    for _, row in df.drop_duplicates().iterrows():
        existing.add((row['country_code'], row['keyword']))
    
    print(f"   Encontradas {len(existing)} combinaciones existentes")
    return existing

def get_missing_combinations():

    print("\n Calculando combinaciones faltantes...")
    all_combinations = set()
    for country_code in COUNTRIES.keys():
        for keyword in FINTECH_KEYWORDS:
            all_combinations.add((country_code, keyword))
    
    print(f"  Total combinaciones esperadas: {len(all_combinations)}")
    

    existing = get_existing_combinations()
    
    missing = all_combinations - existing
    
    print(f"   ❌ Combinaciones faltantes: {len(missing)}")
    print()
    
    if missing:
        missing_by_country = {}
        for country, keyword in missing:
            if country not in missing_by_country:
                missing_by_country[country] = []
            missing_by_country[country].append(keyword)
        
        print("   Detalle de faltantes:")
        for country, keywords in sorted(missing_by_country.items()):
            print(f"      {country}: {len(keywords)} keywords faltantes")
            for kw in keywords:
                print(f"         - {kw}")
        print()
    
    return missing

def extract_missing_data():

    # Extrae SOLO las combinaciones país-keyword que faltan
 
    setup_logging()
    print(" RELLENO INTELIGENTE DE DATOS FALTANTES")

    missing_combinations = get_missing_combinations()
    
    if not missing_combinations:
        print(" ¡No hay datos faltantes! Todos los datos están completos.")
        return
    
    print(f" Extrayendo {len(missing_combinations)} combinaciones faltantes...")
    print()

    response = input("  Continuar con la extracción? (yes/no): ").lower().strip()
    if response not in ['yes', 'y']:
        print("\n Extracción cancelada por el usuario")
        return
    
    print()
    
    all_data = []
    total = len(missing_combinations)
    
    for i, (country_code, keyword) in enumerate(sorted(missing_combinations), 1):
        logging.info(f"[{i}/{total}] Fetching: {keyword} - {country_code}")
        
        try:
            df = fetch_trends_data(keyword, country_code)
            
            if not df.empty:
                all_data.append(df)
                logging.info(f"   {len(df)} registros obtenidos")
            else:
                logging.warning(f"   No data for {keyword} - {country_code}")
            
            # rate limits
            wait_time = random.uniform(15, 25)
            logging.info(f"    Waiting {wait_time:.1f}s before next request...")
            time.sleep(wait_time)
            
        except Exception as e:
            logging.error(f"   Error: {e}")
            continue
    
    print()
    
    if not all_data:
        logging.error(" No data extracted. Aborting.")
        return
    
    # Concatenar todos los datos extraídos
    raw_df = pd.concat(all_data, ignore_index=True)
    logging.info(f" Total raw records extracted: {len(raw_df)}")
    
    # Guardar backup
    backup_path = project_root / "data" / "raw" / "google_trends_missing_raw.csv"
    raw_df.to_csv(backup_path, index=False)
    logging.info(f" Raw data saved to: {backup_path}")
    
    print()
    print(" Transforming data...")
    
    # Transformar
    clean_df = transform_pipeline(raw_df)
    
    if clean_df.empty:
        logging.warning("⚠️ No data after transformation.")
        return
    
    logging.info(f" Clean records after transformation: {len(clean_df)}")
    
    # Guardar clean backup
    clean_path = project_root / "data" / "processed" / "google_trends_missing_clean.csv"
    clean_df.to_csv(clean_path, index=False)
    logging.info(f"💾 Clean data saved to: {clean_path}")
    
    print()
    print(" Uploading to Supabase...")
    print("    Using UPSERT (safe, won't duplicate)")
    print()
    
    # Upload
    upload_dataframe(clean_df)
    
    print(" MISSING DATA EXTRACTION COMPLETED")
    print()
    print("Summary:")
    print(f"   Combinaciones procesadas: {len(missing_combinations)}")
    print(f"   Raw records extracted: {len(raw_df)}")
    print(f"   Clean records: {len(clean_df)}")
    print(f"   Uploaded to Supabase")
    print()

if __name__ == "__main__":
    extract_missing_data()