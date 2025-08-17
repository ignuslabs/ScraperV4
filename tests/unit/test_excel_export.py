"""Unit tests for Excel export functionality."""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from unittest.mock import patch
import pandas as pd

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from src.utils.data_utils import (
    export_to_excel,
    get_export_statistics,
    _clean_column_name,
    _ensure_unique_column_names,
    _convert_value_for_excel,
    _prepare_dataframe_for_excel
)


class TestExcelExport:
    """Test cases for Excel export functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_data = [
            {
                "id": 1,
                "name": "Product A",
                "price": 29.99,
                "details": {"weight": "500g", "color": "red"},
                "tags": ["electronics", "portable"],
                "active": True
            },
            {
                "id": 2,
                "name": "Product B",
                "price": 45.50,
                "details": {"weight": "1kg", "color": "blue"},
                "tags": ["home", "furniture"],
                "active": False
            }
        ]
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('src.utils.data_utils.config')
    def test_export_to_excel_basic(self, mock_config):
        """Test basic Excel export functionality."""
        mock_config.data_folder = self.temp_dir
        
        result_path = export_to_excel(self.test_data, "test_basic.xlsx")
        
        assert Path(result_path).exists()
        assert result_path.endswith('.xlsx')
        
        # Verify content
        df = pd.read_excel(result_path)
        assert len(df) == 2
        assert 'id' in df.columns
        assert 'name' in df.columns
        assert df.iloc[0]['id'] == 1
        assert df.iloc[1]['id'] == 2
    
    @patch('src.utils.data_utils.config')
    def test_export_to_excel_empty_data(self, mock_config):
        """Test Excel export with empty data."""
        mock_config.data_folder = self.temp_dir
        
        result_path = export_to_excel([], "test_empty.xlsx")
        
        assert Path(result_path).exists()
        df = pd.read_excel(result_path)
        assert len(df) == 1
        assert 'No Data' in df.columns
    
    @patch('src.utils.data_utils.config')
    def test_export_to_excel_auto_filename(self, mock_config):
        """Test Excel export with auto-generated filename."""
        mock_config.data_folder = self.temp_dir
        
        result_path = export_to_excel(self.test_data[:1])
        
        assert Path(result_path).exists()
        assert 'export_' in Path(result_path).name
        assert result_path.endswith('.xlsx')
    
    @patch('src.utils.data_utils.config')
    def test_export_to_excel_nested_data_flattening(self, mock_config):
        """Test Excel export with nested data flattening."""
        mock_config.data_folder = self.temp_dir
        
        nested_data = [{
            "id": 1,
            "user": {
                "name": "John",
                "profile": {"age": 30, "city": "NYC"}
            },
            "scores": [100, 95, 87]
        }]
        
        result_path = export_to_excel(nested_data, "test_nested.xlsx")
        
        assert Path(result_path).exists()
        df = pd.read_excel(result_path)
        
        # Check that nested data was flattened
        assert 'user_name' in df.columns
        assert 'user_profile_age' in df.columns
        assert 'user_profile_city' in df.columns
        assert df.iloc[0]['user_name'] == 'John'
    
    @patch('src.utils.data_utils.config')
    def test_export_to_excel_filename_extension(self, mock_config):
        """Test that .xlsx extension is added if missing."""
        mock_config.data_folder = self.temp_dir
        
        result_path = export_to_excel(self.test_data, "test_no_extension")
        
        assert result_path.endswith('.xlsx')
        assert Path(result_path).exists()
    
    @patch('src.utils.data_utils.config')
    def test_export_to_excel_special_characters(self, mock_config):
        """Test Excel export with special characters."""
        mock_config.data_folder = self.temp_dir
        
        special_data = [{
            "name": "Test with éñ@#$%",
            "description": "Special chars: <>&'\"",
            "unicode": "🚀 Unicode test"
        }]
        
        result_path = export_to_excel(special_data, "test_special.xlsx")
        
        assert Path(result_path).exists()
        df = pd.read_excel(result_path)
        assert df.iloc[0]['name'] == "Test with éñ@#$%"
    
    @patch('src.utils.data_utils.config')
    @patch('pandas.ExcelWriter')
    def test_export_to_excel_fallback_on_error(self, mock_writer, mock_config):
        """Test fallback to JSON when Excel export fails."""
        mock_config.data_folder = self.temp_dir
        mock_writer.side_effect = Exception("Excel export failed")
        
        result_path = export_to_excel(self.test_data, "test_fallback.xlsx")
        
        # Should fallback to JSON
        assert result_path.endswith('.json')
        assert Path(result_path).exists()


class TestExcelHelpers:
    """Test helper functions for Excel export."""
    
    def test_clean_column_name_basic(self):
        """Test basic column name cleaning."""
        assert _clean_column_name("normal_name") == "normal_name"
        assert _clean_column_name("name with spaces") == "name_with_spaces"
        assert _clean_column_name("name@#$%special") == "name_special"  # Multiple special chars collapse to single underscore
        assert _clean_column_name("") == "column"
    
    def test_clean_column_name_long(self):
        """Test column name truncation."""
        long_name = "a" * 300
        result = _clean_column_name(long_name)
        assert len(result) <= 255
        assert result.endswith("...")
    
    def test_ensure_unique_column_names(self):
        """Test ensuring unique column names."""
        columns = ["name", "value", "name", "name", "other"]
        unique = _ensure_unique_column_names(columns)
        
        expected = ["name", "value", "name_1", "name_2", "other"]
        assert unique == expected
    
    def test_convert_value_for_excel_basic(self):
        """Test basic value conversion for Excel."""
        assert _convert_value_for_excel(None) == ""
        assert _convert_value_for_excel("string") == "string"
        assert _convert_value_for_excel(42) == 42
        assert _convert_value_for_excel(True) == True
    
    def test_convert_value_for_excel_complex(self):
        """Test complex value conversion for Excel."""
        # Test dict conversion
        result = _convert_value_for_excel({"key": "value"})
        assert '"key": "value"' in result
        
        # Test list conversion
        result = _convert_value_for_excel(["a", "b", "c"])
        assert '["a", "b", "c"]' in result
        
        # Test long string truncation
        long_string = "x" * 40000
        result = _convert_value_for_excel(long_string)
        assert len(result) <= 32767
        assert result.endswith("...")
    
    def test_convert_value_for_excel_datetime(self):
        """Test datetime conversion for Excel."""
        dt = datetime(2025, 1, 1, 12, 0, 0)
        result = _convert_value_for_excel(dt)
        assert result == "2025-01-01T12:00:00"
    
    def test_prepare_dataframe_for_excel(self):
        """Test DataFrame preparation for Excel."""
        df = pd.DataFrame({
            "normal": [1, 2, 3],
            "with_none": [1, None, 3],
            "with_dict": [{"a": 1}, {"b": 2}, {"c": 3}]
        })
        
        result_df = _prepare_dataframe_for_excel(df)
        
        # Check that None values are filled
        assert result_df["with_none"].iloc[1] == ""
        
        # Check that dict values are converted to JSON strings
        assert '"a": 1' in result_df["with_dict"].iloc[0]


class TestGetExportStatistics:
    """Test export statistics functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_get_export_statistics_excel(self):
        """Test getting statistics for Excel files."""
        # Create a test Excel file
        test_data = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})
        excel_path = Path(self.temp_dir) / "test.xlsx"
        test_data.to_excel(excel_path, index=False)
        
        stats = get_export_statistics(str(excel_path))
        
        assert stats["filename"] == "test.xlsx"
        assert stats["format"] == ".xlsx"
        assert stats["record_count"] == 3
        assert stats["file_size"] > 0
        assert "created_at" in stats
    
    def test_get_export_statistics_nonexistent(self):
        """Test getting statistics for non-existent file."""
        stats = get_export_statistics("/nonexistent/file.xlsx")
        assert "error" in stats
        assert stats["error"] == "Export file not found"


if __name__ == "__main__":
    pytest.main([__file__])