import unittest
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.transform import (
    clean_price,
    clean_rating,
    clean_colors,
    clean_size,
    clean_gender,
    clean_title,
    is_valid_product,
    transform_data
)


class TestTransform(unittest.TestCase):
    """Test suite untuk fungsi-fungsi transform"""
    
    def setUp(self):
        self.sample_products = [
            {
                'title': 'Cool T-Shirt',
                'price': '$25.99',
                'rating': '4.5 / 5',
                'colors': '5 Colors',
                'size': 'Size: L',
                'gender': 'Gender: Men'
            },
            {
                'title': 'Smart Jacket',
                'price': '$89.99',
                'rating': '4.8 / 5',
                'colors': '3 Colors',
                'size': 'Size: XL',
                'gender': 'Gender: Women'
            },
            {
                'title': 'Unknown Product',
                'price': 'Price Unavailable',
                'rating': 'Invalid Rating',
                'colors': '0 Colors',
                'size': 'Size: Unknown',
                'gender': 'Gender: Unknown'
            }
        ]
    
    def test_clean_price_valid(self):
        self.assertEqual(clean_price('$25.99'), 25.99 * 16000)
        self.assertEqual(clean_price('$100.00'), 100 * 16000)
    
    def test_clean_price_invalid(self):
        self.assertEqual(clean_price('Price Unavailable'), 0)
        self.assertEqual(clean_price(''), 0)
        self.assertEqual(clean_price(None), 0)
    
    def test_clean_price_with_currency_symbol(self):
        """Test clean_price dengan berbagai format"""
        self.assertEqual(clean_price("$25.99"), 25.99 * 16000)
    
    def test_clean_rating_valid(self):
        self.assertEqual(clean_rating('4.5 / 5'), 4.5)
        self.assertEqual(clean_rating('5 / 5'), 5.0)
    
    def test_clean_rating_invalid(self):
        self.assertEqual(clean_rating('Invalid Rating'), 0)
        self.assertEqual(clean_rating(''), 0)
    
    def test_clean_rating_with_whitespace(self):
        """Test clean_rating dengan spasi ekstra"""
        self.assertEqual(clean_rating(" 4.5 / 5 "), 4.5)
    
    def test_clean_colors_valid(self):
        self.assertEqual(clean_colors('5 Colors'), 5)
        self.assertEqual(clean_colors('10 colors'), 10)
    
    def test_clean_colors_invalid(self):
        self.assertEqual(clean_colors('0 Colors'), 0)
        self.assertEqual(clean_colors(''), 0)
    
    def test_clean_size_valid(self):
        self.assertEqual(clean_size('Size: L'), 'L')
        self.assertEqual(clean_size('Size: XL'), 'XL')
    
    def test_clean_size_invalid(self):
        self.assertEqual(clean_size('Size: Unknown'), 'Unknown')
        self.assertEqual(clean_size(''), 'Unknown')
    
    def test_clean_gender_valid(self):
        self.assertEqual(clean_gender('Gender: Men'), 'Men')
        self.assertEqual(clean_gender('Gender: Women'), 'Women')
    
    def test_clean_gender_invalid(self):
        self.assertEqual(clean_gender('Gender: Unknown'), 'Unknown')
        self.assertEqual(clean_gender(''), 'Unknown')
    
    def test_clean_title_normal(self):
        """Test clean_title dengan judul normal"""
        self.assertEqual(clean_title("Cool Shirt"), "Cool Shirt")
    
    def test_clean_title_invalid(self):
        """Test clean_title dengan judul invalid"""
        self.assertEqual(clean_title("Unknown Product"), "Unknown Product")
        self.assertEqual(clean_title(""), "Unknown Product")
    
    def test_is_valid_product_true(self):
        product = {
            'title': 'Cool T-Shirt',
            'price_rupiah': 415840,
            'rating': 4.5,
            'colors': 5,
            'size': 'L',
            'gender': 'Men'
        }
        self.assertTrue(is_valid_product(product))
    
    def test_is_valid_product_false(self):
        product = {
            'title': 'Unknown Product',
            'price_rupiah': 0,
            'rating': 0,
            'colors': 0,
            'size': 'Unknown',
            'gender': 'Unknown'
        }
        self.assertFalse(is_valid_product(product))
    
    def test_transform_data(self):
        result_df = transform_data(self.sample_products)
        self.assertIsInstance(result_df, pd.DataFrame)
        self.assertIn('Title', result_df.columns)
        self.assertEqual(len(result_df), 2)
    
    def test_transform_data_empty(self):
        result_df = transform_data([])
        self.assertTrue(result_df.empty)

    def test_clean_title_none(self):
        """Test clean_title dengan None"""
        from utils.transform import clean_title
        self.assertEqual(clean_title(None), "Unknown Product")
    
    def test_clean_price_edge_cases(self):
        """Test clean_price dengan format aneh"""
        from utils.transform import clean_price
        self.assertEqual(clean_price("$0.00"), 0.0)
        self.assertEqual(clean_price("$999999.99"), 999999.99 * 16000)

if __name__ == '__main__':
    import logging
    logging.disable(logging.CRITICAL)
    unittest.main()