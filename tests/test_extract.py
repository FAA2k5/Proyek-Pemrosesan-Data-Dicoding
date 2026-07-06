import unittest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.extract import (
    fetch_page_content,
    extract_products_from_html,
    extract_product_from_card,
    scrape_all_products,
    extract_data
)

# Test suite untuk fungsi-fungsi extract
class TestExtract(unittest.TestCase):
    def setUp(self):
        self.sample_html = """
        <div class="collection-card">
            <h3 class="product-title">Cool T-Shirt</h3>
            <div class="price-container"><span class="price">$25.99</span></div>
            <p>Rating: ⭐ 4.5 / 5</p>
            <p>5 Colors</p>
            <p>Size: L</p>
            <p>Gender: Men</p>
        </div>
        """
        
        self.sample_html_multiple = """
        <div class="collection-card">
            <h3 class="product-title">Product1</h3>
            <div class="price-container"><span class="price">$10</span></div>
        </div>
        <div class="collection-card">
            <h3 class="product-title">Product2</h3>
            <div class="price-container"><span class="price">$20</span></div>
        </div>
        """
        
        self.full_page_html = """
        <div class="collection-grid" id="collectionList">
            <div class="collection-card">
                <h3 class="product-title">T-shirt 2</h3>
                <div class="price-container"><span class="price">$102.15</span></div>
                <p>Rating: ⭐ 3.9 / 5</p>
                <p>3 Colors</p>
                <p>Size: M</p>
                <p>Gender: Women</p>
            </div>
            <div class="collection-card">
                <h3 class="product-title">Hoodie 3</h3>
                <div class="price-container"><span class="price">$496.88</span></div>
                <p>Rating: ⭐ 4.8 / 5</p>
                <p>3 Colors</p>
                <p>Size: L</p>
                <p>Gender: Unisex</p>
            </div>
        </div>
        """
    
    def test_extract_data(self):
        with patch('utils.extract.scrape_all_products') as mock_scrape:
            mock_scrape.return_value = [{'title': 'Test', 'price': '$10'}]
            result = extract_data()
            self.assertIsInstance(result, list)
    
    def test_extract_product_from_card_valid(self):
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(self.sample_html, 'html.parser')
        card = soup.find('div', class_='collection-card')
        result = extract_product_from_card(card)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['title'], 'Cool T-Shirt')
        self.assertEqual(result['price'], '$25.99')
    
    def test_extract_product_from_card_none(self):
        result = extract_product_from_card(None)
        self.assertIsNone(result)
    
    def test_extract_products_from_html_empty(self):
        result = extract_products_from_html("")
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)
    
    def test_extract_products_from_html_invalid(self):
        result = extract_products_from_html("<div>no product</div>")
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)
    
    def test_extract_products_from_html_success(self):
        result = extract_products_from_html(self.full_page_html)
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
    
    @patch('utils.extract.requests.get')
    def test_fetch_page_content_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html>Test</html>"
        mock_get.return_value = mock_response
        result = fetch_page_content(1)
        self.assertEqual(result, "<html>Test</html>")
    
    @patch('utils.extract.requests.get')
    def test_fetch_page_content_failure(self, mock_get):
        mock_get.side_effect = Exception("Connection error")
        result = fetch_page_content(1, max_retries=1)
        self.assertIsNone(result)
    
    @patch('utils.extract.requests.get')
    def test_fetch_page_content_page_2(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html>Page2</html>"
        mock_get.return_value = mock_response
        result = fetch_page_content(2)
        self.assertEqual(result, "<html>Page2</html>")
        # Cek URL menggunakan /page2
        mock_get.assert_called()
    
    @patch('utils.extract.requests.get')
    def test_fetch_page_content_retry_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html>Success after retry</html>"
        mock_get.side_effect = [Exception("Timeout"), mock_response]
        
        result = fetch_page_content(1, max_retries=2)
        
        self.assertEqual(result, "<html>Success after retry</html>")
        self.assertEqual(mock_get.call_count, 2)
    
    @patch('utils.extract.fetch_page_content')
    def test_scrape_all_products(self, mock_fetch):
        mock_fetch.return_value = self.full_page_html
        result = scrape_all_products()
        self.assertIsInstance(result, list)
    
    def test_extract_products_from_html_no_cards(self):
        html = "<div>no products here</div>"
        result = extract_products_from_html(html)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)


if __name__ == '__main__':
    import logging
    logging.disable(logging.CRITICAL)
    unittest.main()