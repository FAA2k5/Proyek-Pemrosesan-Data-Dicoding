import pandas as pd
import re
import logging
from typing import List, Dict
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

EXCHANGE_RATE = 16000

# Konversi USD ke Rupiah
def clean_price(price_str: str) -> float:
    try:
        if not price_str or price_str == "Price Unavailable":
            return 0.0
        
        match = re.search(r'\$?([0-9.]+)', price_str)
        if match:
            usd_price = float(match.group(1))
            return round(usd_price * EXCHANGE_RATE, 2)
        return 0.0
    except Exception:
        return 0.0

# Konversi rating ke float
def clean_rating(rating_str: str) -> float:
    try:
        if not rating_str or rating_str == "Invalid Rating":
            return 0.0
        
        if '/' in rating_str:
            rating_value = rating_str.split('/')[0].strip()
        else:
            rating_value = rating_str
        
        return float(rating_value)
    except Exception:
        return 0.0

# Konversi colors ke integer
def clean_colors(colors_str: str) -> int:
    try:
        if not colors_str:
            return 0
        
        match = re.search(r'(\d+)\s*Colors?', colors_str, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return 0
    except Exception:
        return 0

# Pembersihan size dari prefix
def clean_size(size_str: str) -> str:
    try:
        if not size_str:
            return "Unknown"
        
        if size_str.startswith("Size: "):
            return size_str.replace("Size: ", "").strip()
        return size_str.strip()
    except Exception:
        return "Unknown"

# Pembersihan gender dari prefix
def clean_gender(gender_str: str) -> str:
    try:
        if not gender_str:
            return "Unknown"
        
        if gender_str.startswith("Gender: "):
            return gender_str.replace("Gender: ", "").strip()
        return gender_str.strip()
    except Exception:
        return "Unknown"

# Pembersihan title
def clean_title(title_str: str) -> str:
    if not title_str or title_str == "Unknown Product":
        return "Unknown Product"
    return title_str.strip()

# Pengecekan status valid produk
def is_valid_product(product: Dict) -> bool:
    if product.get('title') == "Unknown Product":
        return False
    if product.get('price_rupiah', 0) <= 0:
        return False
    if product.get('rating', 0) <= 0:
        return False
    if product.get('colors', 0) <= 0:
        return False
    if product.get('size') == "Unknown":
        return False
    if product.get('gender') == "Unknown":
        return False
    return True

# Transformasi data utama
def transform_data(raw_products: List[Dict]) -> pd.DataFrame:
    logger.info(f"Memulai transformasi dengan {len(raw_products)} produk mentah")
    
    if not raw_products:
        return pd.DataFrame()
    
    df = pd.DataFrame(raw_products)
    
    df['title'] = df['title'].apply(clean_title)
    df['price_rupiah'] = df['price'].apply(clean_price)
    df['rating'] = df['rating'].apply(clean_rating)
    df['colors'] = df['colors'].apply(clean_colors)
    df['size'] = df['size'].apply(clean_size)
    df['gender'] = df['gender'].apply(clean_gender)
    
    df = df.drop(columns=['price'])
    
    before = len(df)
    df = df.drop_duplicates(subset=['title'], keep='first')
    logger.info(f"Hapus duplikat: {before - len(df)} baris")
    
    valid_mask = df.apply(is_valid_product, axis=1)
    invalid = (~valid_mask).sum()
    df = df[valid_mask]
    logger.info(f"Hapus invalid: {invalid} baris")
    
    df = df.reset_index(drop=True)
    df['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    df = df[['title', 'price_rupiah', 'rating', 'colors', 'size', 'gender', 'timestamp']]
    
    df['price_rupiah'] = df['price_rupiah'].astype(float)
    df['rating'] = df['rating'].astype(float)
    df['colors'] = df['colors'].astype(int)
    
    df = df.rename(columns={
        'title': 'Title',
        'price_rupiah': 'Price',
        'rating': 'Rating',
        'colors': 'Colors',
        'size': 'Size',
        'gender': 'Gender'
    })
    
    df.index = range(1, len(df) + 1)
    
    logger.info(f"Transformasi selesai: {len(df)} produk valid")
    return df


if __name__ == "__main__":
    test_data = [
        {'title': 'T-shirt 2', 'price': '$102.15', 'rating': '3.9 / 5', 
         'colors': '3 Colors', 'size': 'Size: M', 'gender': 'Gender: Women'}
    ]
    result = transform_data(test_data)
    print(result)