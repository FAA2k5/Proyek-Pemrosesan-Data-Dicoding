import requests
import time
import re
import logging
from bs4 import BeautifulSoup
from typing import List, Dict, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

BASE_URL = "https://fashion-studio.dicoding.dev"

# Mengambil konten HTML dari halaman tertentu
def fetch_page_content(page_num: int = 1, max_retries: int = 3) -> Optional[str]:
    if page_num == 1:
        url = BASE_URL
    else:
        url = f"{BASE_URL}/page{page_num}"
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Mengakses {url}")
            response = requests.get(url, headers=HEADERS, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.warning(f"Gagal halaman {page_num}: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                return None
    return None

# Mengekstrak produk dari HTML
def extract_products_from_html(html_content: str) -> List[Dict]:
    products = []
    soup = BeautifulSoup(html_content, 'html.parser')
    
    cards = soup.find_all('div', class_='collection-card')
    
    logger.info(f"Ditemukan {len(cards)} card produk")
    
    for card in cards:
        product = extract_product_from_card(card)
        if product:
            products.append(product)
    
    return products

# Ekstrak data dari satu card produk
def extract_product_from_card(card) -> Optional[Dict]:
    try:
        # Title
        title_elem = card.find('h3', class_='product-title')
        title = title_elem.text.strip() if title_elem else "Unknown Product"
        
        # Price
        price_elem = card.find('span', class_='price')
        if not price_elem:
            price_elem = card.find('p', class_='price')
        price = price_elem.text.strip() if price_elem else "Price Unavailable"
        
        # Rating 
        card_text = card.get_text()
        rating_match = re.search(r'Rating:.*?(\d+\.?\d*)\s*/\s*5', card_text)
        if rating_match:
            rating = f"{rating_match.group(1)} / 5"
        else:
            rating = "Invalid Rating"
        
        # Colors
        colors_match = re.search(r'(\d+)\s*Colors', card_text)
        colors = f"{colors_match.group(1)} Colors" if colors_match else "0 Colors"
        
        # Size
        size_match = re.search(r'Size:\s*([A-Z0-9]+)', card_text)
        size = f"Size: {size_match.group(1)}" if size_match else "Size: Unknown"
        
        # Gender
        gender_match = re.search(r'Gender:\s*([A-Za-z]+)', card_text)
        gender = f"Gender: {gender_match.group(1)}" if gender_match else "Gender: Unknown"
        
        if title == "Unknown Product" or price == "Price Unavailable":
            return None
        
        return {
            'title': title,
            'price': price,
            'rating': rating,
            'colors': colors,
            'size': size,
            'gender': gender
        }
        
    except Exception as e:
        logger.debug(f"Error ekstrak card: {e}")
        return None

# Scrape semua produk dari semua halaman
def scrape_all_products() -> List[Dict]:
    all_products = []
    seen_titles = set()
    
    for page_num in range(1, 51):  # Halaman 1 sampai 50
        logger.info(f"========== MEMPROSES HALAMAN {page_num} ==========")
        
        html = fetch_page_content(page_num)
        if not html:
            logger.warning(f"Halaman {page_num} gagal, berhenti!")
            break
        
        products = extract_products_from_html(html)
        
        if not products:
            logger.warning(f"Halaman {page_num} tidak ada produk!")
            continue
        
        new_count = 0
        for product in products:
            key = f"{product['title']}_{product['price']}"
            if key not in seen_titles:
                seen_titles.add(key)
                all_products.append(product)
                new_count += 1
        
        logger.info(f"Halaman {page_num}: {len(products)} produk, {new_count} baru")
        logger.info(f"Total unik sejauh ini: {len(all_products)}")
        
        time.sleep(0.5)  # Jeda antar request
    
    logger.info(f"========== SELESAI! Total produk: {len(all_products)} ==========")
    return all_products

# Fungsi utama extract
def extract_data() -> List[Dict]:
    logger.info("Memulai ekstraksi data dari fashion-studio.dicoding.dev")
    products = scrape_all_products()
    return products


if __name__ == "__main__":
    data = extract_data()
    print(f"\nTotal produk yg berhasil di-scrape: {len(data)}")
    if data:
        print(f"\nContoh produk pertama:")
        for k, v in data[0].items():
            print(f"  {k}: {v}")