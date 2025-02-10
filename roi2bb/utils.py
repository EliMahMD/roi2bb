import nibabel as nib
import pydicom
import cv2
import numpy as np
import SimpleITK as sitk
from PIL import Image
import os

def load(image_file_path, file_format=None):
    """
    Load a medical image from DICOM, NIfTI, or standard image formats (PNG, JPEG, etc.).
    
    Args:
        image_file_path (str): Path to the image file.
        file_format (str, optional): Manually specify format ("nifti", "dicom", "png", "mha", etc.).
                                     If None, it will infer from the file extension.

    Returns:
        img_data (numpy.ndarray): The image array.
        metadata (dict): A dictionary containing image metadata.
    """
    if file_format is None:
        file_ext = os.path.splitext(image_file_path)[1].lower()
        file_format = {
            ".nii": "nifti",
            ".nii.gz": "nifti",
            ".dcm": "dicom",
            ".png": "png",
            ".jpg": "jpg",
            ".jpeg": "jpg",
            ".bmp": "bmp",
            ".tiff": "tiff",
            ".mha": "mha",
            ".mhd": "mha",
        }.get(file_ext, None)

    metadata = {}

    try:
        if file_format == "nifti":  # NIfTI format
            img = nib.load(image_file_path)
            img_data = img.get_fdata()
            header = img.header
            metadata = {
                "resolution": header.get_zooms(),
                "shape": img.shape,
                "affine": img.affine
            }

        elif file_format == "dicom":  # DICOM format
            dicom_img = pydicom.dcmread(image_file_path)
            img_data = dicom_img.pixel_array
            metadata = {
                "PixelSpacing": dicom_img.get("PixelSpacing", None),
                "Shape": img_data.shape
            }

        elif file_format in ["png", "jpg", "jpeg", "bmp", "tiff"]:  # Standard images
            img = Image.open(image_file_path)
            img_data = np.array(img.convert("L"))  # Convert to grayscale
            metadata = {"shape": img_data.shape}

        elif file_format == "mha":  # MetaImage (MHA/MHD)
            itk_img = sitk.ReadImage(image_file_path)
            img_data = sitk.GetArrayFromImage(itk_img)
            metadata = {
                "resolution": itk_img.GetSpacing(),
                "shape": img_data.shape,
            }
            
        else:
            raise ValueError(f"Unsupported or unknown file format: {file_format}")

    except Exception as e:
        raise RuntimeError(f"Error loading image {image_file_path}: {str(e)}")

    return img_data, metadata
