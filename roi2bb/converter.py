import os
import json
import argparse
from typing import List, Dict, Any, Optional, Tuple
import nibabel as nib
from .utils import (
    load_medical_image,
    generate_class_mapping,
    get_class_index,
    get_json_files,
    extract_class_name
)

class Converter:
    """
    Converts 3D Slicer JSON annotations into YOLO 3D format.
    
    This class handles the conversion of Region of Interest (ROI) bounding boxes
    from 3D Slicer's patient coordinate system to YOLO's image coordinate system.
    It processes JSON annotation files and converts them to normalized YOLO format
    suitable for 3D deep learning models.
    
    Attributes:
        image_file_path (str): Path to the NIfTI image file
        json_folder_path (str): Path to folder containing JSON annotation files
        output_file_path (str): Path to save YOLO 3D format output
        yolo_content (List[str]): Stores YOLO 3D format annotations
        class_mapping (Dict[str, int]): Mapping of class names to indices
    """

    def __init__(self, image_file_path: str, json_folder_path: str, output_file_path: str, class_mapping: Optional[Dict[str, int]] = None):
        """
        Initialize the converter.

        Args:
            image_file_path (str): Path to the NIfTI image file (.nii or .nii.gz)
            json_folder_path (str): Path to folder containing JSON annotation files
            output_file_path (str): Path to save YOLO 3D format output text file
            class_mapping (Optional[Dict[str, int]]): Custom class name to index mapping.
                                                   If None, auto-generates from JSON files.
        
        Raises:
            FileNotFoundError: If image file or JSON folder doesn't exist
            ValueError: If image file format is not supported
        """
        # Validate inputs
        if not os.path.exists(image_file_path):
            raise FileNotFoundError(f"Image file not found: {image_file_path}")
        if not os.path.exists(json_folder_path):
            raise FileNotFoundError(f"JSON folder not found: {json_folder_path}")
        if not os.path.isdir(json_folder_path):
            raise ValueError(f"JSON path must be a directory: {json_folder_path}")
        
        self.image_file_path = image_file_path
        self.json_folder_path = json_folder_path
        self.output_file_path = output_file_path
        self.yolo_content: List[str] = []

        # Load image metadata (resolution, shape, affine transform)
        self.img_data, metadata = load_medical_image(image_file_path)
        self.image_resolution: Optional[Tuple] = metadata.get("resolution", None)
        self.image_shape: Optional[Tuple] = metadata.get("shape", None)
        self.affine: Optional[Any] = metadata.get("affine", None)

        if self.image_resolution and self.image_shape:
            self.image_physical_size_mm = [
                self.image_shape[i] * self.image_resolution[i] for i in range(len(self.image_shape))
            ]
        else:
            raise ValueError("Could not extract image resolution and shape from the medical image")

        if self.affine is not None:
            self.topleft = self.affine[:3, 3]  # Extract origin
            self.topleft[1] *= -1  # Flip Y-axis
            self.topleft[2] *= -1  # Flip Z-axis
        else:
            raise ValueError("Could not extract affine transformation from the medical image")

        # Generate or use provided class mapping
        json_files = get_json_files(self.json_folder_path)
        if not json_files:
            raise ValueError(f"No JSON files found in directory: {json_folder_path}")
        
        if class_mapping is not None:
            self.class_mapping = class_mapping
        else:
            self.class_mapping = generate_class_mapping(json_files)

    def convert_single_roi(self, json_file_path: str) -> None:
        """
        Converts a single ROI from JSON to YOLO 3D format.

        Args:
            json_file_path (str): Path to the ROI JSON file
        
        Raises:
            FileNotFoundError: If JSON file doesn't exist
            KeyError: If JSON structure is invalid
            ValueError: If ROI data is malformed
        """
        if not os.path.exists(json_file_path):
            raise FileNotFoundError(f"JSON file not found: {json_file_path}")
            
        organ_name = extract_class_name(os.path.basename(json_file_path))
        class_index = get_class_index(organ_name, self.class_mapping)
        
        if class_index == -1:
            raise ValueError(f"Unknown class: {organ_name}. Available classes: {list(self.class_mapping.keys())}")

        try:
            with open(json_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format in {json_file_path}: {str(e)}")
        
        try:
            roi = data['markups'][0]
            center = roi['center']
            roi_size_mm = roi['size']
        except (KeyError, IndexError) as e:
            raise KeyError(f"Invalid ROI JSON structure in {json_file_path}: {str(e)}")
        
        if len(center) != 3 or len(roi_size_mm) != 3:
            raise ValueError(f"Invalid ROI dimensions in {json_file_path}. Expected 3D coordinates.")

        # Correct axis directions
        center[0] = -1 * center[0]
        center[2] = -1 * center[2]
        new_center = [self.topleft[i] - center[i] for i in range(3)]

        # Normalize coordinates
        yolo_center = [new_center[i] / self.image_physical_size_mm[i] for i in range(3)]
        yolo_size = [
            roi_size_mm[0] / self.image_physical_size_mm[0],
            roi_size_mm[1] / self.image_physical_size_mm[1],
            roi_size_mm[2] / self.image_physical_size_mm[2]
        ]

        yolo_format = f"{class_index} {yolo_center[2]} {yolo_center[0]} {yolo_center[1]} {yolo_size[2]} {yolo_size[0]} {yolo_size[1]}"
        self.yolo_content.append(yolo_format)

    def process_all_rois(self) -> None:
        """
        Processes all JSON annotation files in the folder.
        
        Raises:
            ValueError: If no JSON files are found or processing fails
        """
        json_file_list = get_json_files(self.json_folder_path)
        if not json_file_list:
            raise ValueError(f"No JSON files found in {self.json_folder_path}")
            
        processed_count = 0
        for json_file_path in json_file_list:
            try:
                self.convert_single_roi(json_file_path)
                processed_count += 1
            except Exception as e:
                print(f"Warning: Failed to process {json_file_path}: {str(e)}")
                continue
                
        if processed_count == 0:
            raise ValueError("No ROI files could be processed successfully")

    def save_output(self) -> None:
        """
        Saves the YOLO 3D annotations to a text file.
        
        Raises:
            IOError: If output file cannot be written
        """
        try:
            # Create output directory if it doesn't exist
            os.makedirs(os.path.dirname(self.output_file_path), exist_ok=True)
            
            with open(self.output_file_path, 'w', encoding='utf-8') as file:
                file.write("\n".join(self.yolo_content))
                
            print(f"Successfully saved {len(self.yolo_content)} annotations to {self.output_file_path}")
        except IOError as e:
            raise IOError(f"Failed to write output file {self.output_file_path}: {str(e)}")

    def run(self) -> None:
        """
        Runs the full conversion process.
        
        This method orchestrates the entire conversion workflow:
        1. Processes all ROI JSON files
        2. Converts them to YOLO format
        3. Saves the output to the specified file
        
        Raises:
            Exception: If any step of the conversion process fails
        """
        try:
            self.process_all_rois()
            if not self.yolo_content:
                raise ValueError("No valid annotations were generated")
            self.save_output()
        except Exception as e:
            raise Exception(f"Conversion failed: {str(e)}")

def main() -> None:
    """
    Command-line interface for converting 3D Slicer JSON annotations to YOLO 3D format.
    
    This function provides a command-line interface for the roi2bb converter,
    allowing users to convert ROI annotations from 3D Slicer to YOLO format
    directly from the terminal.
    """
    parser = argparse.ArgumentParser(description='Convert 3D Slicer ROIs to YOLO 3D bounding box format.')
    parser.add_argument('image_file', type=str, help='Path to the input NIfTI image file (.nii or .nii.gz).')
    parser.add_argument('json_folder', type=str, help='Path to the folder containing the 3D Slicer ROI JSON files.')
    parser.add_argument('output_file', type=str, help='Path to the output YOLO format text file.')

    args = parser.parse_args()

    try:
        # Initialize the converter
        converter = Converter(args.image_file, args.json_folder, args.output_file)

        # Run the conversion process
        converter.run()
        print(f'Successfully converted ROIs from {args.json_folder} and saved YOLO format output to {args.output_file}')
    except Exception as e:
        print(f'Error: {str(e)}')
        exit(1)

if __name__ == '__main__':
    main()
