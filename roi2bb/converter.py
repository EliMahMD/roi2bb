import os
import json
import re
import argparse
import numpy as np
import nibabel as nib
from .utils import (
    convert_bbox_to_yolo_3d,
    map_unique_names,
    get_json_files,
)

class AnnotationConverter:
    """
    Converts 3D Slicer JSON annotations into YOLO 3D format.
    """

    def __init__(self, json_folder_path: str, output_file_path: str, affine: np.ndarray, image_shape: tuple):
        """
        Args:
            json_folder_path (str): Path to the folder containing JSON annotations.
            output_file_path (str): Path to save YOLO 3D format output.
            affine (np.ndarray): Affine transformation matrix from NIfTI header.
            image_shape (tuple): Image dimensions (height, width, depth).
        """
        self.json_folder_path = json_folder_path 
        self.output_file_path = output_file_path #YOLO text file
        self.image_shape = image_shape  # image dimensions are needed to normalize bbox dimensions as YOLO instruction
        self.affine = affine #needed to find origin point's coordinates
        self.yolo_content = [] 
        
        self.topleft = affine[:3, 3]  
        self.topleft[1] *= -1 
        self.topleft[2] *= -1 

    def process_annotations(self):
        json_files = get_json_files(self.json_folder_path)
        unique_name_mapping = map_unique_names(json_files)

        for json_file in json_files:
            json_path = os.path.join(self.json_folder_path, json_file)
            with open(json_path, "r") as f:
                annotation_data = json.load(f)

            base_name = os.path.splitext(json_file)[0]
            match = re.search(r"_(\D+)", base_name)
            organ_name = match.group(1).lower() if match else base_name.lower()
            class_id = unique_name_mapping[organ_name]  

            for annotation in annotation_data.get("annotations", []):
                x, y, z, width, height, depth = (
                    annotation["x"],
                    annotation["y"],
                    annotation["z"],
                    annotation["width"],
                    annotation["height"],
                    annotation["depth"],
                )
                yolo_bbox = convert_bbox_to_yolo_3d(x, y, z, width, height, depth, self.image_shape)

                self.yolo_content.append(f"{class_id} {yolo_bbox}\n")

    def save_to_file(self):
        with open(self.output_file_path, "w") as f:
            f.writelines(self.yolo_content)

def main():
    parser = argparse.ArgumentParser(description="Convert 3D Slicer JSON annotations to YOLO 3D format.")
    parser.add_argument("json_folder_path",type=str,help="Path to the folder containing 3D Slicer JSON annotation files.")
    parser.add_argument("nifti_file",type=str,help="Path to the NIfTI image file (for affine transformation and image dimensions).")
    parser.add_argument("output_file_path",type=str,help="Path to save the YOLO 3D format output text file.")
    args = parser.parse_args()

    nifti_img = nib.load(args.nifti_file)
    affine_matrix = nifti_img.affine
    image_shape = nifti_img.shape 

    # Run the conversion process
    converter = AnnotationConverter(
        json_folder_path=args.json_folder_path,
        output_file_path=args.output_file_path,
        affine=affine_matrix,
        image_shape=image_shape
    )
    converter.process_annotations()
    converter.save_to_file()
    print(f"json coordinates from {args.json_folder_path} was converted to YOLO text format and saved at: {args.output_file_path}")

if __name__ == "__main__":
    main()
