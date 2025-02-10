import os
import nibabel as nib
import re

def load_medical_image(image_file_path):
    """
    Load a medical image from NIfTI format.

    Args:
        image_file_path (str): Path to the image file.

    Returns:
        tuple: (image data as numpy array, metadata dictionary)
    """
    metadata = {}

    try:
        img = nib.load(image_file_path)
        img_data = img.get_fdata()
        metadata = {
            "resolution": img.header.get_zooms(),
            "shape": img.shape,
            "affine": img.affine
        }
    except Exception as e:
        raise RuntimeError(f"Error loading image {image_file_path}: {str(e)}")

    return img_data, metadata

def get_json_files(folder_path):
    """
    Returns a list of JSON files in a given folder.

    Args:
        folder_path (str): Path to the folder.

    Returns:
        list: List of JSON file paths.
    """
    return [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(".json")]

def extract_class_name(filename):
    """
    Extracts the organ name from the filename, ignoring numeric suffixes.

    Args:
        filename (str): JSON filename (e.g., "Patient_002_liver_1.json").

    Returns:
        str: Extracted organ name (e.g., "liver").
    """
    base_name = os.path.splitext(filename)[0]  # Remove .json extension

    # Use regex to extract the organ name (ignoring patient ID and numeric suffixes)
    match = re.search(r"_(\D+)", base_name)
    if match:
        organ_name = match.group(1).lower()  # Convert to lowercase for consistency
    else:
        organ_name = base_name.lower()

    return organ_name

def generate_class_mapping(json_files):
    """
    Generates a mapping of unique class names to a unique number starting from 1.

    Args:
        json_files (list): List of JSON filenames.

    Returns:
        dict: Mapping of class names to unique IDs (starting from 1).
    """
    unique_labels = set()

    for filename in json_files:
        organ_name = extract_class_name(os.path.basename(filename))
        unique_labels.add(organ_name)

    # Assign unique numbers starting from 1
    class_mapping = {label: i + 1 for i, label in enumerate(sorted(unique_labels))}
    
    return class_mapping

def get_class_index(class_label, class_mapping):
    """
    Returns the unique class index for a given class label.

    Args:
        class_label (str): Extracted organ name.
        class_mapping (dict): Mapping of organ names to class IDs.

    Returns:
        int: The assigned class index.
    """
    return class_mapping.get(class_label, -1)  # Return -1 if class not found
