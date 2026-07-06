import sys
import logging
import argparse
import time
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_directories():
    import os
    directories = ['tests', 'utils']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            init_file = os.path.join(directory, '__init__.py')
            if not os.path.exists(init_file):
                with open(init_file, 'w') as f:
                    f.write("# Auto-generated init file\n")


def run_etl_pipeline_separate(save_to_csv=True, save_to_gsheets=False, save_to_postgres=False):
    logger.info("=" * 50)
    logger.info("Memulai ETL Pipeline Fashion Studio")
    logger.info("=" * 50)
    
    # TAHAP 1: EXTRACT
    logger.info("Tahap 1: Pengambilan data dari website")
    try:
        from utils.extract import extract_data
        raw_products = extract_data()
        logger.info(f"Ekstraksi selesai: {len(raw_products)} produk ditemukan")
    except Exception as e:
        logger.error(f"Gagal melakukan ekstraksi: {e}")
        return None, None, None
    
    # TAHAP 2: TRANSFORM
    logger.info("Tahap 2: Transformasi Data")
    try:
        from utils.transform import transform_data
        df_clean = transform_data(raw_products)
        logger.info(f"Hasil transformasi: {len(df_clean)} produk valid")
    except Exception as e:
        logger.error(f"Gagal melakukan transformasi: {e}")
        return raw_products, None, None
    
    # TAHAP 3: LOAD
    logger.info("Tahap 3: Proses penyimpanan ke repositori")
    
    results = {'csv': False, 'google_sheets': False, 'postgresql': False}
    
    from utils.load import load_to_csv, load_to_google_sheets, load_to_postgresql
    
    # Load ke CSV
    if save_to_csv:
        logger.info(">>> Menyimpan ke CSV...")
        results['csv'] = load_to_csv(df_clean)
        logger.info(f"Hasil CSV: {'BERHASIL' if results['csv'] else 'GAGAL'}")
        time.sleep(1)  # Delay 1 detik
    
    # Load ke Google Sheets
    if save_to_gsheets:
        logger.info(">>> Menyimpan ke Google Sheets...")
        results['google_sheets'] = load_to_google_sheets(df_clean)
        logger.info(f"Hasil Google Sheets: {'BERHASIL' if results['google_sheets'] else 'GAGAL'}")
        time.sleep(1)  # Delay 1 detik
    
    # Load ke PostgreSQL
    if save_to_postgres:
        logger.info(">>> Menyimpan ke PostgreSQL...")
        results['postgresql'] = load_to_postgresql(df_clean)
        logger.info(f"Hasil PostgreSQL: {'BERHASIL' if results['postgresql'] else 'GAGAL'}")
        time.sleep(1)  # Delay 1 detik
    
    logger.info("=" * 50)
    logger.info("ETL Pipeline Selesai")
    logger.info("=" * 50)
    
    return raw_products, df_clean, results


def run_etl_pipeline_single(save_to_csv=True, save_to_gsheets=False, save_to_postgres=False):
    logger.info("=" * 50)
    logger.info("Memulai ETL Pipeline Fashion Studio")
    logger.info("=" * 50)
    
    # TAHAP 1: EXTRACT
    logger.info("Tahap 1: Pengambilan data dari website")
    try:
        from utils.extract import extract_data
        raw_products = extract_data()
        logger.info(f"Ekstraksi selesai: {len(raw_products)} produk ditemukan")
    except Exception as e:
        logger.error(f"Gagal melakukan ekstraksi: {e}")
        return None, None, None
    
    # TAHAP 2: TRANSFORM
    logger.info("Tahap 2: Transformasi Data")
    try:
        from utils.transform import transform_data
        df_clean = transform_data(raw_products)
        logger.info(f"Hasil transformasi: {len(df_clean)} produk valid")
        if not df_clean.empty:
            logger.info(f"Preview data:\n{df_clean.head()}")
    except Exception as e:
        logger.error(f"Gagal melakukan transformasi: {e}")
        return raw_products, None, None
    
    # TAHAP 3: LOAD
    logger.info("Tahap 3: Proses penyimpanan ke repositori")
    try:
        from utils.load import load_data
        results = load_data(
            df_clean,
            save_to_csv=save_to_csv,
            save_to_gsheets=save_to_gsheets,
            save_to_postgres=save_to_postgres
        )
    except Exception as e:
        logger.error(f"Gagal melakukan loading: {e}")
        results = {'error': str(e)}
    
    logger.info("=" * 50)
    logger.info("ETL Pipeline Selesai")
    logger.info("=" * 50)
    
    return raw_products, df_clean, results


def main():
    parser = argparse.ArgumentParser(description='ETL Pipeline untuk Fashion Studio')
    parser.add_argument('--csv', action='store_true', default=True, help='Simpan ke CSV (default: True)')
    parser.add_argument('--gsheets', action='store_true', help='Simpan ke Google Sheets')
    parser.add_argument('--postgres', action='store_true', help='Simpan ke PostgreSQL')
    parser.add_argument('--all', action='store_true', help='Simpan ke semua repositori')
    
    args = parser.parse_args()
    
    setup_directories()
    
    if args.all:
        logger.info("MODE: ALL (menyimpan ke semua repositori)")
        
        # Extract dan Transform SEKALI, lalu load ke semua repositori SATU PER SATU
        raw_data, clean_data, results = run_etl_pipeline_separate(
            save_to_csv=True,
            save_to_gsheets=True,
            save_to_postgres=True
        )
    else:

        save_to_csv = args.csv
        save_to_gsheets = args.gsheets
        save_to_postgres = args.postgres
        
        logger.info(f"Target penyimpanan: CSV={save_to_csv}, Google Sheets={save_to_gsheets}, PostgreSQL={save_to_postgres}")
        
        raw_data, clean_data, results = run_etl_pipeline_single(
            save_to_csv=save_to_csv,
            save_to_gsheets=save_to_gsheets,
            save_to_postgres=save_to_postgres
        )
    
    # Ringkasan
    if clean_data is not None and not clean_data.empty:
        print("\n" + "=" * 50)
        print("RINGKASAN HASIL ETL")
        print("=" * 50)
        print(f"Jumlah data mentah (extract): {len(raw_data) if raw_data else 0}")
        print(f"Jumlah data bersih (transform): {len(clean_data)}")
        print(f"Data duplikat & invalid dihapus: {(len(raw_data) - len(clean_data)) if raw_data else 0}")
        print(f"\nHasil penyimpanan (load):")
        for repo, status in results.items():
            if repo != 'error':
                print(f"  - {repo}: {'BERHASIL' if status else 'GAGAL'}")
        print("=" * 50)
        
        # Tampilkan 5 data pertama
        print("\n5 Data Pertama:")
        print(clean_data.head().to_string())
    elif clean_data is not None and clean_data.empty:
        print("\nTidak ada data valid yang dihasilkan")
    else:
        print("\nETL Pipeline gagal")
    
    return clean_data


if __name__ == "__main__":
    main()