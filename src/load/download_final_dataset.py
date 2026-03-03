
import pandas as pd
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.load.supabase_loader import get_supabase_client

def download_final_dataset():
    print(" DESCARGA DE DATASET FINAL DESDE SUPABASE")
    
    print(" Conectando a Supabase...")
    client = get_supabase_client()
    
    all_data = []
    page_size = 1000
    offset = 0
    
    while True:
        response = client.table("fintech_trends")\
            .select("*")\
            .range(offset, offset + page_size - 1)\
            .order("date")\
            .execute()
        
        if not response.data:
            break
        
        all_data.extend(response.data)
        print(f"   Descargados: {len(all_data)} registros...")
        
        offset += page_size
        
        if len(response.data) < page_size:
            break
    
    # Convertir a DataFrame
    df = pd.DataFrame(all_data)
    
    # Ordenar por fecha, país, keyword
    df = df.sort_values(['date', 'country_code', 'keyword'])
    
    # Seleccionar columnas relevantes (sin id, created_at)
    columns_to_save = ['date', 'keyword', 'country_code', 'interest_score', 'z_score']
    df_final = df[columns_to_save].copy()
    
    # Guardar
    final_path = project_root / "data" / "processed" / "google_trends_final.csv"
    df_final.to_csv(final_path, index=False)
    
    print()
    print(" DATASET FINAL DESCARGADO")
    print()
    print(f" Total registros: {len(df_final):,}")
    print(f" Guardado en: {final_path}")
    print()
    print(" Resumen por país:")
    summary = df_final.groupby('country_code').agg({
        'keyword': 'nunique',
        'date': 'count'
    }).rename(columns={'keyword': 'keywords', 'date': 'records'})
    print(summary)
    print()
    
if __name__ == "__main__":
    download_final_dataset()