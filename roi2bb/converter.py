import os
import json
import re
from .utils import (
    convert_bbox_to_yolo,
    map_unique_names,
    get_json_files,
)

class roi2bb:
    """
    Converts 3D Slicer JSON annotations into YOLO format.
    """

    def __init__(self, json_folder_path: str, output_file_path: str, image_shape: tuple):
        """
        Initialize the converter.

        Args:
            json_folder_path (str): Path to the folder containing JSON annotations.
            output_file_path (str): Path to save YOLO format output.
            image_shape (tuple): Image dimensions (height, width).
        """
        self.json_folder_path = json_folder_path
        self.output_file_path = output_file_path
        self.image_shape = image_shape 
        self.yolo_content = [] 

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

            base_name = os.path.splitext(json_file)[0]
            match = re.search(r"_(\D+)", base_name)
            organ_name = match.group(1).lower() if match else base_name.lower()
            class_id = unique_name_mapping[organ_name]  

            for annotation in annotation_data.get("annotations", []):
                x, y, width, height = annotation["x"], annotation["y"], annotation["width"], annotation["height"]
                yolo_bbox = convert_bbox_to_yolo(x, y, width, height, self.image_shape)

                self.yolo_content.append(f"{class_id} {yolo_bbox}\n")

    def save_to_file(self):
        """
        Saves the YOLO annotations to a text file.
        """
        with open(self.output_file_path, "w") as f:
            f.writelines(self.yolo_content)
