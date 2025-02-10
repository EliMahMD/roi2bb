import os
import json
import argparse
import glob
import nibabel as nib
from .utils import (
    load_medical_image,
    generate_class_mapping,
    get_class_index,
    get_json_files,
    extract_class_name
)

class AnnotationConverter:
    """
    Converts 3D Slicer JSON annotations into YOLO 3D format.
    """

    def __init__(self, image_file_path: str, json_folder_path: str, output_file_path: str):
        """
        Initialize the converter.

        Args:
            image_file_path (str): Path to the NIfTI image.
            json_folder_path (str): Path to folder containing JSON annotation files.
            output_file_path (str): Path to save YOLO 3D format output.
        """
        self.image_file_path = image_file_path
        self.json_folder_path = json_folder_path
        self.output_file_path = output_file_path
        self.yolo_content = []  # Stores YOLO 3D format annotations

        # Load image metadata (resolution, shape, affine transform)
        self.img_data, metadata = load_medical_image(image_file_path)
        self.image_resolution = metadata.get("resolution", None)
        self.image_shape = metadata.get("shape", None)
        self.affine = metadata.get("affine", None)

        if self.image_resolution and self.image_shape:
            self.image_physical_size_mm = [
                self.image_shape[i] * self.image_resolution[i] for i in range(len(self.image_shape))
            ]

        if self.affine is not None:
            self.topleft = self.affine[:3, 3]  # Extract origin
            self.topleft[1] *= -1  # Flip Y-axis
            self.topleft[2] *= -1  # Flip Z-axis

        # Generate class mapping
        json_files = get_json_files(self.json_folder_path)
        self.class_mapping = generate_class_mapping(json_files)

    def convert_single_roi(self, json_file_path: str):
        """
        Converts a single ROI from JSON to YOLO 3D format.

        Args:
            json_file_path (str): Path to the ROI JSON file.
        """
        organ_name = extract_class_name(os.path.basename(json_file_path))
        class_index = get_class_index(organ_name, self.class_mapping)

        with open(json_file_path, 'r') as file:
            json_data = file.read()
        data = json.loads(json_data)

        roi = data['markups'][0]
        center = roi['center']
        roi_size_mm = roi['size']

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

    def process_all_rois(self):
        """
        Processes all JSON annotation files in the folder.
        """
        json_file_list = get_json_files(self.json_folder_path)
        for json_file_path in json_file_list:
            self.convert_single_roi(json_file_path)

    def save_output(self):
        """
        Saves the YOLO 3D annotations to a text file.
        """
        with open(self.output_file_path, 'w') as file:
            file.write("\n".join(self.yolo_content))

    def run(self):
        """
        Runs the full conversion process.
        """
        self.process_all_rois()
        self.save_output()

def main():
    """
    Command-line interface for converting 3D Slicer JSON annotations to YOLO 3D format.
    """
    parser = argparse.ArgumentParser(description='Convert 3D Slicer ROIs to YOLO 3D bounding box format.')
    parser.add_argument('image_file', type=str, help='Path to the input NIfTI image file (.nii or .nii.gz).')
    parser.add_argument('json_folder', type=str, help='Path to the folder containing the 3D Slicer ROI JSON files.')
    parser.add_argument('output_file', type=str, help='Path to the output YOLO format text file.')

    args = parser.parse_args()

    # Initialize the converter
    converter = AnnotationConverter(args.image_file, args.json_folder, args.output_file)

    # Run the conversion process
    converter.run()
    print(f'Converted ROIs from {args.json_folder} and saved YOLO format output to {args.output_file}')

if __name__ == '__main__':
    main()
