# roi2bb
### "3D Slicer ROI" to "YOLO Bounding Box" Coordinates Converter for Medical Imaging
This repository provides a Python class, `roi2bb`, bridging the gap between ground truth preparation and model training for 3D volumetric medical imaging, by converting Regions of Interest (ROI) bounding boxes stored in 3D Slicer JSON format into YOLO models input format. 

When it comes to volumetric medical imaging data, there are few tools (if any) available for 3D bounding box annotation. 3D Slicer is a robust open-source tool for all types of data visualization, processing and annotation. 3D Slicer's **ROI** function of [**markups** module](https://slicer.readthedocs.io/en/latest/user_guide/modules/markups.html), offers a user-friendly interface to generate 3D bounding boxes around the object/region of interest, edit and rotate them in axial, coronal and sagittal planes for object-oriented tasks and visualize them in 3D view. The central coordinates and the dimensions of these ROI boxes can be extracted as a JSON file, but the output is not compatible with the "Image coordinates System", which is the format compatible with the well-known YOLO family of deep learning models.  

These two [coordinate systems](https://slicer.readthedocs.io/en/latest/user_guide/coordinate_systems.html) have 3 main differences that should be addressed while converting:

1. The Slicer output follows the **"Patient coordinate system"**, in which its origin is located at an anatomical landmark not necessarily in the image boundaries, while the YOLO-compatible input format is based on the **"Image coordinate system"**, in which its origin is located at the upper-left corner of the image. Also, the axis directions are not the same in different coordinate systems, changing the point coordinate values. By origin, we mean the point of x, y, z = [0, 0, 0].
.    
2. Width, height and depth in the Slicer output is the actual values in the metric system (mm, cm), while width, height and depth in the Yolo input are a ratio of full image dimensions (in the range of 0 to 1). 

3. The Slicer output is in JSON format with the ROI 'center' coordinates (x,y,z) and ROI dimensions 'size' (x_length, y_length,z_length) reported under 'markups' tag, while YOLO-compatible input is a text file with each line presenting one bounding box containing: 

    ```"class center_z center_x center_y width height depth"```

    The Slicer gives a separate JSON file for each ROI, while a single YOLO text file contains multiple ROIs for multiple classes, each class defined by a unique index and each ROI reported in a separate line.
     
roi2bb offers CLI support for single annotations and python API for several images and multi-class annotations. 

## Table of Contents:

- [Requirements](#requirements)
- [Installation](#installation)
    - [Directory Structure](#directory-structure)
    - [Class Index Mapping](#class-index-mapping)
    - [Example Usage](#usage)
- [License](#license)
- [Useful Links](#Useful-Links)

## Requirements:

- Python 3.x
- os
- glob
- numpy
- json
- argparse
- nibabel/pydicom/PIL/cv2/SimpleITK #depending on your images format

## Installation
```bash
pip install roi2bb
```
or directly from GitHub:

```bash
# Clone the repository
git clone https://github.com/EliMahMD/roi2bb.git
cd roi2bb
```
Here is a stepwise guide to use `roi2bb`:

### Directory Structure:
YOLO expects coordinates in form of a single .txt per image, containing all labels of all classes. To generate such output, roi2bb has to process all json files corresponding to a single image, at once. 
To do so, roi2bb expects the below structure for images and labels. It automatically defines unique class IDs (1,2,3) by mapping the unique classes detected in JSON file names. You can also define your desired mapping using the Python API or modify the Converter class to be compatible with your data.

```
project_directory/
├── images/
│   ├── Patient_001.nii or .nii.gz
│   ├── Patient_002.nii
│   │──...
├── labels/
│   ├── Patient_001/
│   │   ├── left_atrium.json
│   │   ├── lymph_node_1.json
│   │   ├── lymph_node_2.json
│   │   ├── lymph_node_3.json
│   │   └── trachea.json
│   ├── Patient_002/
│   │   ├── left_atrium.json
│   │   ├── lymph_node.json
│   │   └── trachea.json
│   │── ...
|   └── Patient_n
└── output/
    │── Patient_001.txt
    │── Patient_002.txt
    |── ...
    └── Patient_n
```
### Class Index Mapping:

converter = roi2bb("path_to_image_file.nii", "path_to_json_folder", "output_yolo_format.txt", class_map:dic = class_map)

```bash
class_map = {
    "left_atrium": 1,
    "lymph_node": 2,
    "trachea": 3,
    ...
    }
```
### Example Usage:

Now that you installed the package, organized your data and customized your labels, you can use the following commands in a command line interface (CLI) or the next one in a Python interface to convert ROIs to YOLO format by `roi2bb`:

**CLI**
```bash
roi2bb example.nii.gz annotations/ output.txt 
```
**Python API**
```bash
from roi2bb.converter import Converter

image_files_list = Path to the medical images
json_folders_list = Folders containing the 3D Slicer JSON annotation files corresponding to ptient_n
output_files_list = Path to save the .txt outputs containing the YOLO format annotations

for image_file_path, json_folder_path, output_file_path in zip(image_files_list, json_folders_list, output_files_list)
    converter = Converter(image_file_path, json_folder_path, output_file_path)
    converter.run()
```

### Example Output:
```bash
0 0.523 0.312 0.532 0.128 0.276 0.345  # left_atrium
1 0.734 0.512 0.723 0.132 0.254 0.367  # lymph_node_1
1 0.834 0.612 0.823 0.152 0.274 0.447  # lymph_node_2
2 0.634 0.412 0.623 0.112 0.234 0.287  # trachea
```
### License:

```roi2bb``` is released under the MIT License. See the [LICENSE](LICENSE) for more details.

### Useful Links

[3D Slicer web page](https://www.slicer.org/) for volumetric medical imaging annotation

[Learn more about the coordinates systems](https://slicer.readthedocs.io/en/latest/user_guide/coordinate_systems.html)


### Contact:

Developer: Elham Mahmoudi

Email: mahmoudi.elham91@gmail.com

Please cite us, if you used roi2bb: [Mahmoudi E, Nagaraja V, Sarraf M, Friedman P, Alkhouli M, Eleid MF, Singh M, Attia ZI, Sobek JD, Naderian M, Nugen F. Fully Automated Aortic Root Localization and Tilt Alignment in Cardiac Computed Tomography. Journal of the Society for Cardiovascular Angiography & Interventions. 2025 Jul 23:103716.](https://www.sciencedirect.com/science/article/pii/S2772930325011585)

GitHub: [https://github.com/elimah91/roi2bb](https://github.com/elimah91/roi2bb)

