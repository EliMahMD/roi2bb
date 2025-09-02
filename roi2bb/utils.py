import os
import re
from typing import Dict, List, Tuple, Any
import nibabel as nib

def load_medical_image(image_file_path: str) -> Tuple[Any, Dict[str, Any]]:
    """
    Load a medical image from NIfTI format.

    Args:
        image_file_path (str): Path to the image file (.nii or .nii.gz)

    Returns:
        Tuple[Any, Dict[str, Any]]: Tuple containing:
            - image data as numpy array
            - metadata dictionary with 'resolution', 'shape', and 'affine' keys
    
    Raises:
        FileNotFoundError: If the image file doesn't exist
        RuntimeError: If the image cannot be loaded or processed
    """
    if not os.path.exists(image_file_path):
        raise FileNotFoundError(f"Image file not found: {image_file_path}")
    
    if not (image_file_path.endswith('.nii') or image_file_path.endswith('.nii.gz')):
        raise ValueError(f"Unsupported file format. Expected .nii or .nii.gz, got: {image_file_path}")
    
    metadata: Dict[str, Any] = {}

    try:
        img = nib.load(image_file_path)
        img_data = img.get_fdata()
        metadata = {
            "resolution": img.header.get_zooms(),
            "shape": img.shape,
            "affine": img.affine
        }
        
        # Validate that we have 3D data
        if len(img.shape) != 3:
            raise ValueError(f"Expected 3D image data, got {len(img.shape)}D")
            
    except Exception as e:
        raise RuntimeError(f"Error loading image {image_file_path}: {str(e)}")

    return img_data, metadata

def get_json_files(folder_path: str) -> List[str]:
    """
    Returns a list of JSON files in a given folder.

    Args:
        folder_path (str): Path to the folder containing JSON files

    Returns:
        List[str]: List of JSON file paths
    
    Raises:
        FileNotFoundError: If the folder doesn't exist
        ValueError: If the path is not a directory
    """
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Folder not found: {folder_path}")
    
    if not os.path.isdir(folder_path):
        raise ValueError(f"Path is not a directory: {folder_path}")
    
    try:
        json_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(".json")]
        return sorted(json_files)  # Sort for consistent processing order
    except PermissionError:
        raise PermissionError(f"Permission denied accessing folder: {folder_path}")

def extract_class_name(filename: str) -> str:
    """
    Extracts the organ name from the filename, ignoring numeric suffixes.

    Args:
        filename (str): JSON filename (e.g., "Patient_002_liver_1.json" or "liver.json")

    Returns:
        str: Extracted organ name (e.g., "liver")
    
    Raises:
        ValueError: If filename is empty or invalid
    """
    if not filename:
        raise ValueError("Filename cannot be empty")
    
    base_name = os.path.splitext(filename)[0]  # Remove .json extension
    
    if not base_name:
        raise ValueError("Invalid filename format")

    # Use regex to extract the organ name (ignoring patient ID and numeric suffixes)
    # First try to find pattern like "Patient_002_liver_1" -> "liver"
    match = re.search(r"_(\D+?)(_\d+)?$", base_name)
    if match:
        organ_name = match.group(1).lower()  # Convert to lowercase for consistency
    else:
        # If no underscore pattern found, use the entire base name
        # Remove any trailing numbers: "liver1" -> "liver"
        organ_name = re.sub(r'\d+$', '', base_name).lower()
    
    # Clean up any remaining underscores or spaces
    organ_name = organ_name.strip('_').replace('_', ' ').strip()
    
    if not organ_name:
        raise ValueError(f"Could not extract valid class name from filename: {filename}")

    return organ_name

def generate_class_mapping(json_files: List[str]) -> Dict[str, int]:
    """
    Generates a mapping of unique class names to a unique number starting from 0.

    Args:
        json_files (List[str]): List of JSON file paths

    Returns:
        Dict[str, int]: Mapping of class names to unique IDs (starting from 0)
    
    Raises:
        ValueError: If no valid class names can be extracted
    """
    if not json_files:
        raise ValueError("No JSON files provided for class mapping generation")
    
    unique_labels = set()

    for filepath in json_files:
        try:
            filename = os.path.basename(filepath)
            organ_name = extract_class_name(filename)
            unique_labels.add(organ_name)
        except ValueError as e:
            print(f"Warning: Skipping file {filepath}: {str(e)}")
            continue
    
    if not unique_labels:
        raise ValueError("No valid class names could be extracted from JSON files")

    # Assign unique numbers starting from 0 (YOLO convention)
    class_mapping = {label: i for i, label in enumerate(sorted(unique_labels))}
    
    print(f"Generated class mapping: {class_mapping}")
    return class_mapping

def get_class_index(class_label: str, class_mapping: Dict[str, int]) -> int:
    """
    Returns the unique class index for a given class label.

    Args:
        class_label (str): Extracted organ name
        class_mapping (Dict[str, int]): Mapping of organ names to class IDs

    Returns:
        int: The assigned class index, or -1 if class not found
    
    Raises:
        ValueError: If class_label is empty or class_mapping is invalid
    """
    if not class_label:
        raise ValueError("Class label cannot be empty")
    
    if not isinstance(class_mapping, dict):
        raise ValueError("Class mapping must be a dictionary")
    
    return class_mapping.get(class_label, -1)  # Return -1 if class not found
