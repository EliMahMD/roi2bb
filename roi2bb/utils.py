import os
import re

def convert_bbox_to_yolo(x, y, width, height, img_shape):
    """
    Converts 3D bounding box from absolute coordinates to YOLO format.

    Args:
        x (float): X coordinate (top-left).
        y (float): Y coordinate (top-left).
        width (float): Box width.
        height (float): Box height.
        img_shape (tuple): Image shape (height, width).

    Returns:
        str: YOLO formatted bounding box string.
    """
    img_height, img_width = img_shape[:2]
    x_center = (x + width / 2) / img_width
    y_center = (y + height / 2) / img_height
    width_norm = width / img_width
    height_norm = height / img_height

    return f"{x_center:.6f} {y_center:.6f} {width_norm:.6f} {height_norm:.6f}"

def get_json_files(folder_path):
    """
    Returns a list of JSON files in a given folder.

    Args:
        folder_path (str): Path to the folder.

    Returns:
        list: List of JSON filenames.
    """
    return [f for f in os.listdir(folder_path) if f.endswith(".json")]

def map_unique_names(json_files):
    """
    Maps unique organ names (ignoring numeric suffixes) to a unique number.

    Args:
        json_files (list): List of JSON filenames.

    Returns:
        dict: Mapping of organ names to unique class IDs.
    """
    unique_labels = set()

    for filename in json_files:
        base_name = os.path.splitext(filename)[0]

        # Extract organ name (ignore numeric suffixes)
        match = re.search(r"_(\D+)", base_name)
        if match:
            organ_name = match.group(1).lower()  # Convert to lowercase
        else:
            organ_name = base_name.lower()

        unique_labels.add(organ_name)

    # Assign unique numeric labels
    label_mapping = {label: i + 1 for i, label in enumerate(sorted(unique_labels))}
    
    return label_mapping
