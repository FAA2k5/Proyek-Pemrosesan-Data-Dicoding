import pandas as pd
import logging
import os
from typing import Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Menyimpan DataFrame ke file CSV
def load_to_csv(df: pd.DataFrame, filename: str = "products.csv") -> bool:
    try:
        if df.empty:
            logger.warning("Tidak ada yang disimpan ke CSV")
            return False
        
        df.to_csv(filename, index=False, encoding='utf-8')
        logger.info(f"Data berhasil disimpan ke {filename} ({len(df)} baris)")
        return True
        
    except Exception as e:
        logger.error(f"Gagal menyimpan ke CSV: {e}")
        return False

# Menyimpan DataFrame ke Google Sheets
def load_to_google_sheets(df: pd.DataFrame, credentials_file: str = "google-sheets-api.json", 
                          spreadsheet_id: Optional[str] = None) -> bool:
    try:
        from google.oauth2.service_account import Credentials
        from googleapiclient.discovery import build
        
        if df.empty:
            logger.warning("DataFrame kosong, tidak ada yang disimpan ke Google Sheets")
            return False
        
        if not os.path.exists(credentials_file):
            logger.error(f"File credentials {credentials_file} tidak ditemukan")
            return False
        
        SPREADSHEET_ID = "1bKTb-7Yd6pymCx13IQmgJY45Yb872u5yq35d6iuCIAI"
        
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        credential = Credentials.from_service_account_file(credentials_file, scopes=SCOPES)
        
        service = build('sheets', 'v4', credentials=credential)
        sheet = service.spreadsheets()
        
        expected_columns = ['Title', 'Price', 'Rating', 'Colors', 'Size', 'Gender']
        
        if list(df.columns) != expected_columns:
         
            available_cols = list(df.columns)
            for col in expected_columns:
                if col not in available_cols:

                    lower_col = col.lower()
                    if lower_col in available_cols:
                        df = df.rename(columns={lower_col: col})
            
            df = df[expected_columns]
        
        values = df.values.tolist()
        body = {'values': values}
        
        RANGE_NAME = 'Sheet1!A2:F'
        
        result = sheet.values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME,
            valueInputOption='RAW',
            body=body
        ).execute()
        
        logger.info(f"Data berhasil disimpan ke Google Sheets")
        logger.info(f"Updated range: {result.get('updatedRange')}")
        logger.info(f"Updated cells: {result.get('updatedCells')}")
        logger.info(f"URL: https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}")
        
        return True
        
    except Exception as e:
        logger.error(f"Gagal menyimpan ke Google Sheets: {e}")
        return False

# Menyimpan DataFrame ke PostgreSQL
def load_to_postgresql(df: pd.DataFrame, db_url: Optional[str] = None) -> bool:
    try:
        from sqlalchemy import create_engine, text
        
        if df.empty:
            logger.warning("Tidak ada yang disimpan ke PostgreSQL")
            return False
        
        if not db_url:
            db_url = "postgresql://faa2005:fairuzganteng@localhost:5432/fashiondb"
        
        logger.info(f"🔄 Mencoba koneksi ke PostgreSQL")
        
        engine = create_engine(db_url)
        
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            logger.info("Koneksi ke PostgreSQL berhasil")
        
        df.to_sql('fashion_products', engine, if_exists='append', index=False)
        
        logger.info(f"Data berhasil disimpan ke PostgreSQL ({len(df)} baris)")
        return True
        
    except ImportError as e:
        logger.error(f"SQLAlchemy atau psycopg2-binary tidak terinstal: {e}")
        return False
    except Exception as e:
        logger.error(f"Gagal menyimpan ke PostgreSQL: {e}")
        return False

# Penyimpanan data ke berbagai repositori
def load_data(df: pd.DataFrame, save_to_csv: bool = True, 
              save_to_gsheets: bool = False, 
              save_to_postgres: bool = False,
              gsheets_credentials: str = "google-sheets-api.json",
              postgres_url: Optional[str] = None) -> dict:
    
    results = {
        'csv': False,
        'google_sheets': False,
        'postgresql': False
    }
    
    if save_to_csv:
        results['csv'] = load_to_csv(df)
    
    if save_to_gsheets:
        results['google_sheets'] = load_to_google_sheets(df, gsheets_credentials)
    
    if save_to_postgres:
        results['postgresql'] = load_to_postgresql(df, postgres_url)
    
    logger.info(f"Hasil penyimpanan: {results}")
    return results