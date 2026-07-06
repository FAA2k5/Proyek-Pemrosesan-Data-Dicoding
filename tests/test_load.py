import unittest
import pandas as pd
import os
import sys
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.load import load_to_csv, load_data


class TestLoad(unittest.TestCase):
    """Test suite untuk fungsi-fungsi load"""
    
    def setUp(self):
        """Setup sebelum setiap test"""
        self.test_df = pd.DataFrame({
            'title': ['Cool T-Shirt', 'Smart Jacket'],
            'price_rupiah': [415840.0, 1439840.0],
            'rating': [4.5, 4.8],
            'colors': [5, 3],
            'size': ['L', 'XL'],
            'gender': ['Men', 'Women'],
            'timestamp': ['2024-01-01 10:00:00', '2024-01-01 10:00:00']
        })
        self.test_filename = "test_output.csv"
    
    def tearDown(self):
        """Bersihkan setelah setiap test"""
        if os.path.exists(self.test_filename):
            os.remove(self.test_filename)
    
    def test_load_to_csv_success(self):
        """Test load_to_csv berhasil menyimpan"""
        result = load_to_csv(self.test_df, self.test_filename)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.test_filename))
        
        df_loaded = pd.read_csv(self.test_filename)
        self.assertEqual(len(df_loaded), len(self.test_df))
    
    def test_load_to_csv_empty_df(self):
        """Test load_to_csv dengan DataFrame kosong"""
        empty_df = pd.DataFrame()
        result = load_to_csv(empty_df, self.test_filename)
        self.assertFalse(result)
    
    @patch('utils.load.load_to_csv')
    def test_load_data_csv_only(self, mock_csv):
        """Test load_data hanya ke CSV"""
        mock_csv.return_value = True
        
        results = load_data(self.test_df, save_to_csv=True, save_to_gsheets=False, save_to_postgres=False)
        
        self.assertTrue(results['csv'])
        self.assertFalse(results['google_sheets'])
        self.assertFalse(results['postgresql'])
    
    @patch('utils.load.load_to_csv')
    @patch('utils.load.load_to_google_sheets')
    def test_load_data_all_repos(self, mock_gsheets, mock_csv):
        """Test load_data ke semua repositori"""
        mock_csv.return_value = True
        mock_gsheets.return_value = True
        
        results = load_data(self.test_df, save_to_csv=True, save_to_gsheets=True, save_to_postgres=False)
        
        self.assertTrue(results['csv'])
        self.assertTrue(results['google_sheets'])
    
    def test_load_data_empty_dataframe(self):
        """Test load_data dengan DataFrame kosong"""
        empty_df = pd.DataFrame()
        results = load_data(empty_df)
        
        self.assertFalse(results['csv'])
    
    @patch('builtins.open', side_effect=IOError("Permission denied"))
    def test_load_to_csv_io_error(self, mock_open):
        """Test load_to_csv dengan IO error"""
        result = load_to_csv(self.test_df, "invalid/path/file.csv")
        self.assertFalse(result)
    
    def test_load_to_google_sheets_file_not_found(self):
        """Test Google Sheets dengan file credentials tidak ditemukan"""
        from utils.load import load_to_google_sheets
        result = load_to_google_sheets(self.test_df, "non_existent.json")
        self.assertFalse(result)
        
    @patch('utils.load.load_to_postgresql')
    def test_load_to_postgresql_called(self, mock_postgres):
        """Test bahwa load_to_postgresql dipanggil saat save_to_postgres=True"""
        mock_postgres.return_value = True
        results = load_data(self.test_df, save_to_postgres=True)
        mock_postgres.assert_called_once()
        self.assertTrue(results['postgresql'])

if __name__ == '__main__':
    import logging
    logging.disable(logging.CRITICAL)
    unittest.main()
