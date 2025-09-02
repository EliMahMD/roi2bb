"""
Unit tests for the roi2bb converter module.
"""
import os
import json
import tempfile
import unittest
from unittest.mock import patch, MagicMock
import numpy as np

from roi2bb.converter import Converter


class TestConverter(unittest.TestCase):
    """Test cases for the Converter class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directories
        self.test_dir = tempfile.mkdtemp()
        self.image_path = os.path.join(self.test_dir, "test_image.nii.gz")
        self.json_dir = os.path.join(self.test_dir, "annotations")
        self.output_path = os.path.join(self.test_dir, "output.txt")
        
        os.makedirs(self.json_dir)
        
        # Create a mock JSON file
        self.sample_json_data = {
            "markups": [{
                "center": [10.0, 20.0, 30.0],
                "size": [5.0, 8.0, 6.0]
            }]
        }
        
        self.json_file_path = os.path.join(self.json_dir, "liver.json")
        with open(self.json_file_path, 'w') as f:
            json.dump(self.sample_json_data, f)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_dir)
    
    @patch('roi2bb.converter.load_medical_image')
    def test_init_valid_inputs(self, mock_load_image):
        """Test Converter initialization with valid inputs."""
        # Mock the image loading
        mock_load_image.return_value = (
            np.zeros((100, 100, 100)),
            {
                "resolution": (1.0, 1.0, 1.0),
                "shape": (100, 100, 100),
                "affine": np.eye(4)
            }
        )
        
        # Create a dummy image file
        with open(self.image_path, 'w') as f:
            f.write("dummy")
        
        converter = Converter(self.image_path, self.json_dir, self.output_path)
        
        self.assertEqual(converter.image_file_path, self.image_path)
        self.assertEqual(converter.json_folder_path, self.json_dir)
        self.assertEqual(converter.output_file_path, self.output_path)
        self.assertIsInstance(converter.class_mapping, dict)
    
    def test_init_nonexistent_image(self):
        """Test Converter initialization with nonexistent image file."""
        with self.assertRaises(FileNotFoundError):
            Converter("nonexistent.nii.gz", self.json_dir, self.output_path)
    
    def test_init_nonexistent_json_dir(self):
        """Test Converter initialization with nonexistent JSON directory."""
        with open(self.image_path, 'w') as f:
            f.write("dummy")
        
        with self.assertRaises(FileNotFoundError):
            Converter(self.image_path, "nonexistent_dir", self.output_path)
    
    @patch('roi2bb.converter.load_medical_image')
    def test_convert_single_roi(self, mock_load_image):
        """Test converting a single ROI."""
        # Mock the image loading
        mock_load_image.return_value = (
            np.zeros((100, 100, 100)),
            {
                "resolution": (1.0, 1.0, 1.0),
                "shape": (100, 100, 100),
                "affine": np.array([[1, 0, 0, 50], [0, -1, 0, 50], [0, 0, -1, 50], [0, 0, 0, 1]])
            }
        )
        
        # Create a dummy image file
        with open(self.image_path, 'w') as f:
            f.write("dummy")
        
        converter = Converter(self.image_path, self.json_dir, self.output_path)
        converter.convert_single_roi(self.json_file_path)
        
        self.assertEqual(len(converter.yolo_content), 1)
        self.assertIsInstance(converter.yolo_content[0], str)
    
    @patch('roi2bb.converter.load_medical_image')
    def test_process_all_rois(self, mock_load_image):
        """Test processing all ROIs in directory."""
        # Mock the image loading
        mock_load_image.return_value = (
            np.zeros((100, 100, 100)),
            {
                "resolution": (1.0, 1.0, 1.0),
                "shape": (100, 100, 100),
                "affine": np.array([[1, 0, 0, 50], [0, -1, 0, 50], [0, 0, -1, 50], [0, 0, 0, 1]])
            }
        )
        
        # Create additional JSON files
        kidney_json_path = os.path.join(self.json_dir, "kidney.json")
        with open(kidney_json_path, 'w') as f:
            json.dump(self.sample_json_data, f)
        
        # Create a dummy image file
        with open(self.image_path, 'w') as f:
            f.write("dummy")
        
        converter = Converter(self.image_path, self.json_dir, self.output_path)
        converter.process_all_rois()
        
        self.assertEqual(len(converter.yolo_content), 2)
    
    @patch('roi2bb.converter.load_medical_image')
    def test_save_output(self, mock_load_image):
        """Test saving output to file."""
        # Mock the image loading
        mock_load_image.return_value = (
            np.zeros((100, 100, 100)),
            {
                "resolution": (1.0, 1.0, 1.0),
                "shape": (100, 100, 100),
                "affine": np.array([[1, 0, 0, 50], [0, -1, 0, 50], [0, 0, -1, 50], [0, 0, 0, 1]])
            }
        )
        
        # Create a dummy image file
        with open(self.image_path, 'w') as f:
            f.write("dummy")
        
        converter = Converter(self.image_path, self.json_dir, self.output_path)
        converter.yolo_content = ["0 0.5 0.5 0.5 0.1 0.1 0.1"]
        converter.save_output()
        
        self.assertTrue(os.path.exists(self.output_path))
        with open(self.output_path, 'r') as f:
            content = f.read().strip()
        self.assertEqual(content, "0 0.5 0.5 0.5 0.1 0.1 0.1")
    
    @patch('roi2bb.converter.load_medical_image')
    def test_custom_class_mapping(self, mock_load_image):
        """Test using custom class mapping."""
        # Mock the image loading
        mock_load_image.return_value = (
            np.zeros((100, 100, 100)),
            {
                "resolution": (1.0, 1.0, 1.0),
                "shape": (100, 100, 100),
                "affine": np.eye(4)
            }
        )
        
        # Create a dummy image file
        with open(self.image_path, 'w') as f:
            f.write("dummy")
        
        custom_mapping = {"liver": 5}
        converter = Converter(self.image_path, self.json_dir, self.output_path, class_mapping=custom_mapping)
        
        self.assertEqual(converter.class_mapping, custom_mapping)


if __name__ == '__main__':
    unittest.main()