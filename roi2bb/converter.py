import os
import json
import re
import numpy as np
from .utils import (
    convert_bbox_to_yolo,
    map_unique_names,
    get_json_files,
)

class AnnotationConverter:
    """
    Converts 3D Slicer JSON annotations into YOLO format with 3D coordinate corrections.
    """

    def __init__(self, json_folder_path: str, output_file_path: str, affine: np.ndarray, image_shape: tuple):
        """
        Initialize the converter.

        Args:
            json_folder_path (str): Path to the folder containing JSON annotations.
            output_file_path (str): Path to save YOLO format output.
            affine (np.ndarray): Affine transformation matrix from NIfTI header.
            image_shape (tuple): Image dimensions (height, width, depth).
        """
        self.json_folder_path = json_folder_path
        self.output_file_path = output_file_path
        self.image_shape = image_shape  # Needed for YOLO bbox conversion
        self.affine = affine  # Needed for coordinate transformations
        self.yolo_content = []  # Stores YOLO format annotations

        # Compute the top-left corner in image coordinate system
        self.topleft = affine[:3, 3]  # Extract origin
        self.topleft[1] *= -1  # Flip Y-axis
        self.topleft[2] *= -1  # Flip Z-axis

    def process_annotations(self):
        """
        Processes all JSON annotation files in the folder and converts them to YOLO format.
        """
        json_files = get_json_files(self.json_folder_path)
        unique_name_mapping = map_unique_names(json_files)

        for json_file in json_files:
            json_path = os.path.join(self.json_folder_path, json_file)
            with open(json_path, "r") as f:
                annotation_data = json.load(f)

            # Extract organ name from filename and assign a class ID
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

                # Convert 3D coordinates to 2D projection for YOLO
                x, y = self.convert_3d_to_2d(x, y, z)

                # Convert to YOLO format
                yolo_bbox = convert_bbox_to_yolo(x, y, width, height, self.image_shape)

                self.yolo_content.append(f"{class_id} {yolo_bbox}\n")

    def convert_3d_to_2d(self, x, y, z):
        """
        Converts 3D coordinates to 2D by applying affine transformation.

        Args:
            x (float): X-coordinate in 3D space.
            y (float): Y-coordinate in 3D space.
            z (float): Z-coordinate in 3D space.

        Returns:
            tuple: Transformed (x, y) in 2D projection.
        """
        coord_3d = np.array([x, y, z, 1])
        transformed = np.dot(self.affine, coord_3d)[:3]  # Apply affine transformation
        transformed[1] *= -1  # Flip Y-axis
        transformed[2] *= -1  # Flip Z-axis
        return transformed[0], transformed[1]  # Return 2D projection (x, y)

    def save_to_file(self):
        """
        Saves the YOLO annotations to a text file.
        """
        with open(self.output_file_path, "w") as f:
            f.writelines(self.yolo_content)
