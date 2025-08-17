"""Security tests for DataService to prevent path traversal attacks."""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
from src.services.data_service import DataService


class TestDataServiceSecurity:
    """Test security aspects of DataService."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = DataService()
        self.service.result_storage = Mock()
        
    def test_sanitize_filename_component_removes_dangerous_chars(self):
        """Test that dangerous characters are removed from filename components."""
        dangerous_inputs = [
            "../../../etc/passwd",
            "../../",
            "../",
            "job..//..\\",
            "job\\..\\",
            "job<script>",
            "job|rm -rf",
            "job;rm -rf",
            "job&rm -rf",
            "job`rm -rf`",
            "job$(rm -rf)",
        ]
        
        for dangerous_input in dangerous_inputs:
            result = self.service._sanitize_filename_component(dangerous_input)
            # Should only contain alphanumeric, underscore, or hyphen
            assert all(c.isalnum() or c in ['_', '-'] for c in result)
            # Should not contain path traversal sequences
            assert '..' not in result
            assert '/' not in result
            assert '\\' not in result

    def test_sanitize_filename_component_length_limit(self):
        """Test that filename components are limited in length."""
        long_input = "a" * 100
        result = self.service._sanitize_filename_component(long_input, max_length=10)
        assert len(result) == 10

    def test_sanitize_filename_component_empty_input(self):
        """Test that empty input results in default value."""
        result = self.service._sanitize_filename_component("")
        assert result == "unknown"
        
        result = self.service._sanitize_filename_component("../../../")
        assert result == "unknown"  # All chars removed, should default

    def test_validate_export_format_allows_safe_formats(self):
        """Test that safe export formats are allowed."""
        safe_formats = ['csv', 'json', 'xlsx', 'txt']
        
        for format_str in safe_formats:
            result = self.service._validate_export_format(format_str)
            assert result == format_str.lower()

    def test_validate_export_format_rejects_dangerous_formats(self):
        """Test that dangerous export formats are rejected."""
        dangerous_formats = [
            'exe',
            'bat',
            'sh',
            'ps1',
            '../csv',
            'csv/../',
            'csv/../../etc/passwd',
            'csv;rm -rf',
        ]
        
        for dangerous_format in dangerous_formats:
            with pytest.raises(ValueError):
                self.service._validate_export_format(dangerous_format)

    def test_validate_export_format_case_insensitive(self):
        """Test that format validation is case insensitive."""
        assert self.service._validate_export_format('CSV') == 'csv'
        assert self.service._validate_export_format('Json') == 'json'
        assert self.service._validate_export_format('XLSX') == 'xlsx'

    @patch('src.core.config.config')
    @patch('src.services.data_service.Path')
    def test_export_job_results_sanitizes_inputs(self, mock_path, mock_config):
        """Test that export_job_results sanitizes malicious inputs."""
        # Mock config and path
        mock_config.data_folder = "/tmp/test"
        mock_export_dir = Mock()
        mock_path.return_value.__truediv__.return_value = mock_export_dir
        mock_export_dir.mkdir.return_value = None
        
        # Mock result storage
        self.service.result_storage.get_results_by_job.return_value = [
            {"id": "1", "data": {"test": "value"}}
        ]
        
        # Test with malicious job_id and format
        malicious_job_id = "../../../etc/passwd"
        malicious_format = "../sh"
        
        # Should raise ValueError for invalid format
        with pytest.raises(ValueError):
            self.service.export_job_results(malicious_job_id, malicious_format)

    def test_sanitize_inputs_integration(self):
        """Test that sanitization works correctly with real examples."""
        # Test sanitizing dangerous job IDs
        dangerous_job_ids = [
            "../../../etc/passwd",
            "job/../../../root",
            "job;rm -rf /",
            "job|cat /etc/passwd",
            "job`whoami`",
            "job$(id)",
        ]
        
        for dangerous_id in dangerous_job_ids:
            sanitized = self.service._sanitize_filename_component(dangerous_id)
            # Should not contain dangerous characters
            assert ".." not in sanitized
            assert "/" not in sanitized
            assert "\\" not in sanitized
            assert ";" not in sanitized
            assert "|" not in sanitized
            assert "`" not in sanitized
            assert "$" not in sanitized
            # Should start with job if the original did
            if dangerous_id.startswith("job"):
                assert sanitized.startswith("job")
            
        # Test format validation
        safe_formats = ["csv", "json", "xlsx", "txt"]
        for fmt in safe_formats:
            validated = self.service._validate_export_format(fmt)
            assert validated == fmt.lower()
        
        # Test dangerous formats
        dangerous_formats = ["../csv", "csv/..", "csv;rm", "exe", "bat"]
        for fmt in dangerous_formats:
            with pytest.raises(ValueError):
                self.service._validate_export_format(fmt)

    def test_filename_sanitization_preserves_valid_chars(self):
        """Test that valid characters are preserved in sanitization."""
        valid_job_id = "job_123-test"
        result = self.service._sanitize_filename_component(valid_job_id)
        assert result == "job_123-test"

    def test_security_headers_in_docstrings(self):
        """Verify security methods have proper documentation."""
        assert "prevent path traversal" in self.service._sanitize_filename_component.__doc__.lower()
        assert "sanitize" in self.service._validate_export_format.__doc__.lower()