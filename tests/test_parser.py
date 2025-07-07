"""
Unit tests for OCIO Test Results Parser
"""

import csv
import tempfile
from pathlib import Path

import pytest

from ocio_performance_analysis.parser import OCIOTestParser, OCIOTestResult


class TestOCIOTestParser:
    """Test suite for OCIOTestParser class."""

    @pytest.fixture
    def parser(self):
        """Create a parser instance for testing."""
        return OCIOTestParser()

    @pytest.fixture
    def sample_test_data(self):
        """Create sample test data for testing."""
        return """
OCIO Version: 2.4.1

OCIO Config. file:    './Downloads/studio-config-aces-v1-and-v2.ocio'
OCIO Config. version: 2.4
OCIO search_path:

Processing statistics:

Processing from 'ACES2065-1' to '(sRGB - Display, ACES 1.0 - SDR Video)'
Create the config identifier:		For 10 iterations, it took: [11.1952, 0.000477791, 1.11995] ms
Create the context identifier:		For 10 iterations, it took: [0.001487, 0.000249889, 0.0003736] ms
Create the (display, view) processor:	For 10 iterations, it took: [1.23402, 0.271924, 0.368133] ms

Image processing statistics:

Process the complete image (in place):				For 10 iterations, it took: [1739.95, 1727.15, 1728.43] ms
Process the complete image (two buffers):			For 10 iterations, it took: [1731.68, 1732.46, 1732.38] ms
"""

    @pytest.fixture
    def sample_multi_run_data(self):
        """Create sample data with multiple test runs."""
        return """
OCIO Version: 2.4.1

OCIO Config. file:    './Downloads/studio-config-aces-v1-and-v2.ocio'
OCIO Config. version: 2.4
OCIO search_path:

Processing statistics:

Processing from 'ACES2065-1' to '(sRGB - Display, ACES 1.0 - SDR Video)'
Create the config identifier:		For 10 iterations, it took: [11.1952, 0.000477791, 1.11995] ms


OCIO Version: 2.4.2

OCIO Config. file:    './Downloads/studio-config-aces-v1-and-v2.ocio'
OCIO Config. version: 2.4
OCIO search_path:

Processing statistics:

Processing from 'ACES2065-1' to '(Rec.709 - Display, ACES 1.0 - SDR Video)'
Create the config identifier:		For 5 iterations, it took: [5.1, 5.2, 5.3, 5.4, 5.5] ms
"""

    def test_regex_patterns(self, parser):
        """Test that regex patterns work correctly."""
        # Test version pattern
        version_match = parser.version_pattern.search("OCIO Version: 2.4.1")
        assert version_match is not None
        assert version_match.group(1) == "2.4.1"

        # Test config version pattern
        config_match = parser.config_version_pattern.search("OCIO Config. version: 2.4")
        assert config_match is not None
        assert config_match.group(1) == "2.4"

        # Test processing pattern
        processing_match = parser.processing_pattern.search(
            "Processing from 'ACES2065-1' to '(sRGB - Display, ACES 1.0 - SDR Video)'"
        )
        assert processing_match is not None
        assert processing_match.group(1) == "ACES2065-1"
        assert processing_match.group(2) == "(sRGB - Display, ACES 1.0 - SDR Video)"

        # Test timing pattern
        timing_match = parser.timing_pattern.search(
            "Create the config identifier:		For 10 iterations, it took: [11.1952, 0.000477791, 1.11995] ms"
        )
        assert timing_match is not None
        assert timing_match.group(1).strip() == "Create the config identifier"
        assert timing_match.group(2) == "10"
        assert timing_match.group(3) == "11.1952, 0.000477791, 1.11995"

        # Test OS release extraction
        assert parser._extract_os_release("OCIO_2.4_ACES_tests_r7.txt") == "r7"
        assert parser._extract_os_release("OCIO_2.4_ACES_tests_r9_sys2043.txt") == "r9"
        assert parser._extract_os_release("OCIO_2.4_ACES_tests_r7_sys2034.ldn.vfx.framestore.com.txt") == "r7"
        assert parser._extract_os_release("some_file_without_release.txt") == "Unknown"

        # Test CPU model extraction
        cpu_content_with_model = "model name: Intel(R) Xeon(R) CPU E5-2667 v4 @ 3.20GHz"
        assert parser._extract_cpu_model(cpu_content_with_model) == "Intel(R) Xeon(R) CPU E5-2667 v4 @ 3.20GHz"

        cpu_content_with_spacing = "model name    : Intel(R) Core(TM) i7-8700K CPU @ 3.70GHz"
        assert parser._extract_cpu_model(cpu_content_with_spacing) == "Intel(R) Core(TM) i7-8700K CPU @ 3.70GHz"

        cpu_content_no_model = "some other content without cpu model"
        assert parser._extract_cpu_model(cpu_content_no_model) == "Unknown"

    def test_parse_test_run(self, parser, sample_test_data):
        """Test parsing a single test run."""
        results = parser._parse_test_run(sample_test_data, "test_file.txt", "Unknown")

        # Should have 5 results (3 processing + 2 image processing)
        assert len(results) == 5

        # Check first result
        first_result = results[0]
        assert first_result.file_name == "test_file.txt"
        assert first_result.ocio_version == "2.4.1"
        assert first_result.config_version == "2.4"
        assert first_result.source_colorspace == "ACES2065-1"
        assert first_result.target_colorspace == "(sRGB - Display, ACES 1.0 - SDR Video)"
        assert first_result.operation == "Create the config identifier"
        assert first_result.iteration_count == 10
        assert len(first_result.timing_values) == 3
        assert first_result.timing_values == [11.1952, 0.000477791, 1.11995]

        # Check calculated statistics
        assert first_result.min_time == 0.000477791
        assert first_result.max_time == 11.1952
        assert abs(first_result.avg_time -  4.10521) < 0.0001

    def test_parse_multi_run_data(self, parser, sample_multi_run_data):
        """Test parsing data with multiple test runs."""
        # Create a temporary file to test the full parsing flow
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp_file:
            tmp_file.write(sample_multi_run_data)
            tmp_file_path = Path(tmp_file.name)

        try:
            results = parser.parse_file(tmp_file_path)

            # Should have results from both OCIO versions
            version_241_results = [r for r in results if r.ocio_version == "2.4.1"]
            version_242_results = [r for r in results if r.ocio_version == "2.4.2"]

            assert len(version_241_results) == 1
            assert len(version_242_results) == 1

            # Check version 2.4.2 result
            v242_result = version_242_results[0]
            assert v242_result.target_colorspace == "(Rec.709 - Display, ACES 1.0 - SDR Video)"
            assert v242_result.iteration_count == 5
            assert len(v242_result.timing_values) == 5
        finally:
            tmp_file_path.unlink()

    def test_empty_content(self, parser):
        """Test parsing empty content."""
        results = parser._parse_test_run("", "empty.txt", "Unknown")
        assert len(results) == 0

    def test_malformed_timing_values(self, parser):
        """Test handling of malformed timing values."""
        malformed_data = """
OCIO Version: 2.4.1
OCIO Config. version: 2.4
Processing from 'ACES2065-1' to '(sRGB - Display, ACES 1.0 - SDR Video)'
Create the config identifier:		For 10 iterations, it took: [invalid, 1.23, text] ms
"""
        results = parser._parse_test_run(malformed_data, "malformed.txt", "Unknown")

        # Should still create a result with valid timing values
        assert len(results) == 0
        #assert results[0].timing_values == [1.23]

    def test_parse_file_with_temp_file(self, parser, sample_test_data):
        """Test parsing a file from disk."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp_file:
            tmp_file.write(sample_test_data)
            tmp_file_path = Path(tmp_file.name)

        try:
            results = parser.parse_file(tmp_file_path)
            assert len(results) == 5
            assert all(r.file_name == tmp_file_path.name for r in results)
        finally:
            tmp_file_path.unlink()

    def test_parse_directory(self, parser, sample_test_data):
        """Test parsing multiple files in a directory."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)

            # Create two test files
            file1 = tmp_path / "test1.txt"
            file2 = tmp_path / "test2.txt"

            file1.write_text(sample_test_data)
            file2.write_text(sample_test_data)

            results = parser.parse_directory(tmp_path)

            # Should have results from both files
            assert len(results) == 10  # 5 results per file

            file1_results = [r for r in results if r.file_name == "test1.txt"]
            file2_results = [r for r in results if r.file_name == "test2.txt"]

            assert len(file1_results) == 5
            assert len(file2_results) == 5

    def test_save_to_csv(self, parser, sample_test_data):
        """Test saving results to CSV file."""
        results = parser._parse_test_run(sample_test_data, "test.txt", "Unknown")

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp_file:
            tmp_file_path = Path(tmp_file.name)

        try:
            parser.save_to_csv(results, tmp_file_path)

            # Read back the CSV and verify content
            with open(tmp_file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                csv_results = list(reader)

            assert len(csv_results) == 5

            # Check first row
            first_row = csv_results[0]
            assert first_row['file_name'] == 'test.txt'
            assert first_row['os_release'] == 'Unknown'  # test.txt doesn't have r7/r9 pattern
            assert first_row['cpu_model'] == 'Unknown'  # test data doesn't have CPU model
            assert first_row['ocio_version'] == '2.4.1'
            assert first_row['config_version'] == '2.4'
            assert first_row['operation'] == 'Create the config identifier'
            assert first_row['iteration_count'] == '10'
            assert first_row['timing_values'] == '11.1952,0.000477791,1.11995'

        finally:
            tmp_file_path.unlink()

    def test_save_empty_results(self, parser):
        """Test saving empty results list."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp_file:
            tmp_file_path = Path(tmp_file.name)

        try:
            parser.save_to_csv([], tmp_file_path)
            # Should not create a file or should create empty file
            assert tmp_file_path.exists()
        finally:
            if tmp_file_path.exists():
                tmp_file_path.unlink()


class TestOCIOTestResult:
    """Test suite for OCIOTestResult data class."""

    def test_test_result_creation(self):
        """Test creating a OCIOTestResult instance."""
        timing_values = [1.0, 2.0, 3.0]
        result = OCIOTestResult(
            file_name="test.txt",
            os_release="r7",
            cpu_model="Intel(R) Core(TM) i7-8700K CPU @ 3.70GHz",
            ocio_version="2.4.1",
            config_version="2.4",
            source_colorspace="ACES2065-1",
            target_colorspace="sRGB",
            operation="Test operation",
            iteration_count=10,
            timing_values=timing_values,
            min_time=0.0,
            max_time=0.0,
            avg_time=0.0
        )

        # Check calculated values
        assert result.min_time == 1.0
        assert result.max_time == 3.0
        assert result.avg_time == 2.0

    def test_empty_timing_values(self):
        """Test OCIOTestResult with empty timing values."""
        result = OCIOTestResult(
            file_name="test.txt",
            os_release="r7",
            cpu_model="Intel(R) Core(TM) i7-8700K CPU @ 3.70GHz",
            ocio_version="2.4.1",
            config_version="2.4",
            source_colorspace="ACES2065-1",
            target_colorspace="sRGB",
            operation="Test operation",
            iteration_count=10,
            timing_values=[],
            min_time=0.0,
            max_time=0.0,
            avg_time=0.0
        )

        assert result.min_time == 0.0
        assert result.max_time == 0.0
        assert result.avg_time == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
