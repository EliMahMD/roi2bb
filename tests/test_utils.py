"""
Unit tests for the roi2bb utils module.
"""
import os
import json
import tempfile
import unittest
from unittest.mock import patch, MagicMock
import numpy as np

from roi2bb.utils import (
    load_medical_image,
    get_json_files,
    extract_class_name,
    generate_class_mapping,
    get_class_index
)


class TestUtils(unittest.TestCase):
    """Test cases for utility functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_extract_class_name_simple(self):
        """Test extracting class name from simple filename."""
        result = extract_class_name("liver.json")
        self.assertEqual(result, "liver")
    
    def test_extract_class_name_with_patient_id(self):
        """Test extracting class name with patient ID."""
        result = extract_class_name("Patient_001_liver_1.json")
        self.assertEqual(result, "liver")
    
    def test_extract_class_name_with_numbers(self):
        """Test extracting class name with trailing numbers."""
        result = extract_class_name("liver123.json")
        self.assertEqual(result, "liver")
    
    def test_extract_class_name_empty_filename(self):
        """Test extracting class name from empty filename."""
        with self.assertRaises(ValueError):
            extract_class_name("")
    
    def test_extract_class_name_complex_pattern(self):
        """Test extracting class name from complex pattern."""
        result = extract_class_name("Patient_002_lymph_node_3.json")
        self.assertEqual(result, "lymph node")
    
    def test_get_json_files_valid_directory(self):
        """Test getting JSON files from valid directory."""
        # Create test JSON files
        json_files = ["liver.json", "kidney.json", "test.txt"]
        for filename in json_files:
            filepath = os.path.join(self.test_dir, filename)
            with open(filepath, 'w') as f:
                f.write("{}")
        
        result = get_json_files(self.test_dir)
        expected_json_files = [
            os.path.join(self.test_dir, "kidney.json"),
            os.path.join(self.test_dir, "liver.json")
        ]
        
        self.assertEqual(len(result), 2)
        self.assertEqual(sorted(result), sorted(expected_json_files))
    
    def test_get_json_files_nonexistent_directory(self):
        """Test getting JSON files from nonexistent directory."""
        with self.assertRaises(FileNotFoundError):
            get_json_files("nonexistent_directory")
    
    def test_get_json_files_not_directory(self):
        """Test getting JSON files from file path instead of directory."""
        test_file = os.path.join(self.test_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("test")
        
        with self.assertRaises(ValueError):
            get_json_files(test_file)
    
    def test_generate_class_mapping_basic(self):
        """Test generating class mapping from JSON files."""
        json_files = [
            os.path.join(self.test_dir, "liver.json"),
            os.path.join(self.test_dir, "kidney.json"),
            os.path.join(self.test_dir, "liver_2.json")
        ]
        
        result = generate_class_mapping(json_files)
        expected = {"kidney": 0, "liver": 1}
        
        self.assertEqual(result, expected)
    
    def test_generate_class_mapping_empty_list(self):
        """Test generating class mapping from empty list."""
        with self.assertRaises(ValueError):
            generate_class_mapping([])
    
    def test_generate_class_mapping_complex_names(self):
        """Test generating class mapping with complex names."""
        json_files = [
            "Patient_001_left_atrium.json",
            "Patient_002_lymph_node_1.json",
            "Patient_003_lymph_node_2.json"
        ]
        
        result = generate_class_mapping(json_files)
        expected = {"left atrium": 0, "lymph node": 1}
        
        self.assertEqual(result, expected)
    
    def test_get_class_index_valid(self):
        """Test getting class index for valid class."""
        class_mapping = {"liver": 0, "kidney": 1}
        result = get_class_index("liver", class_mapping)
        self.assertEqual(result, 0)
    
    def test_get_class_index_invalid(self):
        """Test getting class index for invalid class."""
        class_mapping = {"liver": 0, "kidney": 1}
        result = get_class_index("heart", class_mapping)
        self.assertEqual(result, -1)
    
    def test_get_class_index_empty_label(self):
        """Test getting class index with empty label."""
        class_mapping = {"liver": 0}
        with self.assertRaises(ValueError):
            get_class_index("", class_mapping)
    
    def test_get_class_index_invalid_mapping(self):
        """Test getting class index with invalid mapping."""
        with self.assertRaises(ValueError):
            get_class_index("liver", "not_a_dict")
    
    @patch('nibabel.load')
    def test_load_medical_image_success(self, mock_nib_load):
        """Test successful loading of medical image."""
        # Mock nibabel objects
        mock_img = MagicMock()
        mock_img.get_fdata.return_value = np.zeros((100, 100, 100))
        mock_img.shape = (100, 100, 100)
        mock_img.header.get_zooms.return_value = (1.0, 1.0, 1.0)
        mock_img.affine = np.eye(4)
        mock_nib_load.return_value = mock_img
        
        # Create dummy file
        test_file = os.path.join(self.test_dir, "test.nii.gz")
        with open(test_file, 'w') as f:
            f.write("dummy")
        
        img_data, metadata = load_medical_image(test_file)
        
        self.assertEqual(img_data.shape, (100, 100, 100))
        self.assertIn("resolution", metadata)
        self.assertIn("shape", metadata)
        self.assertIn("affine", metadata)
    
    def test_load_medical_image_nonexistent_file(self):
        """Test loading nonexistent medical image."""
        with self.assertRaises(FileNotFoundError):
            load_medical_image("nonexistent.nii.gz")
    
    def test_load_medical_image_invalid_format(self):
        """Test loading medical image with invalid format."""
        test_file = os.path.join(self.test_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("dummy")
        
        with self.assertRaises(ValueError):
            load_medical_image(test_file)


if __name__ == '__main__':
    unittest.main()