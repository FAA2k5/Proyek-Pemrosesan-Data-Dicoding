import requests
from bs4 import BeautifulSoup

URL = "https://fashion-studio.dicoding.dev?page=1"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

response = requests.get(URL, headers=HEADERS)
soup = BeautifulSoup(response.text, 'html.parser')

# Cari semua div dengan class
all_divs = soup.find_all('div')
print(f"Total div: {len(all_divs)}")

# Cari yang mengandung $
dollar_elements = soup.find_all(string=lambda x: x and '$' in str(x))
print(f"Elemen mengandung $: {len(dollar_elements)}")

# Cari class yang mengandung 'product'
product_classes = []
for div in all_divs:
    classes = div.get('class', [])
    for cls in classes:
        if 'product' in cls.lower():
            product_classes.append(cls)

print(f"Class mengandung 'product': {set(product_classes)}")

# Tampilkan sample HTML dari div pertama yang mengandung $
for elem in dollar_elements[:3]:
    print(f"\nParent: {elem.parent.name}")
    print(f"Parent class: {elem.parent.get('class')}")
    print(f"Text: {elem[:100]}")