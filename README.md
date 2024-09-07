# roi2bb
### "3D Slicer ROI" to "YOLO Bounding Box" Coordinates Converter
This repository provides a Python class, `roi2bb`, bridging the gap between ground truth preparation and model training for 3D volumetric medical imaging, by converting Regions of Interest (ROI) bounding boxes stored in 3D Slicer JSON format into YOLO models input format. 

When it comes to volumetric medical imaging data, there are few tools (if any) available for 3D bounding box annotation. 3D Slicer's **ROI** function of [**markups** module](https://slicer.readthedocs.io/en/latest/user_guide/modules/markups.html), offers a user-friendly interface to generate 3D bounding boxes around the object/region of interest, edit them in axial, coronal and sagittal views, rotate them for object-oriented tasks and visualize them in 3D view. The central coordinates and the dimensions of these ROI boxes can be extracted as a JSON file, but the output is not compatible with the more commonly used "Image coordinates System", which is the format compatible with the well-known YOLO models. 

These two [coordinate systems](https://slicer.readthedocs.io/en/latest/user_guide/coordinate_systems.html) have 3 main differences that should be addressed while converting:

1. The Slicer output follows the **"Patient coordinate system"**, in which its origin is located at an anatomical landmark not necessarily in the image boundaries, while the YOLO-compatible input format is based on the **"Image coordinate system"**, in which its origin is located at the upper-left corner of the image. Also, the axis directions are not the same in different coordinate systems, changing the point coordinate values.
    
2. The Slicer format dimensions are the actual ROI dimensions, while the Yolo format dimensions are a ratio of ROI dimension to image dimensions. 

3. The Slicer output is in JSON format with the ROI 'center' coordinates (x,y,z) and ROI dimensions 'size' (x_length, y_length,z_length) reported under 'markups' tag, while YOLO-compatible input is a text file with each line presenting one ROI containing: 

    ```"class center_z center_x center_y length_z length_x length_y"```

    The Slicer gives one JSON file for each ROI, while a single YOLO text file contains multiple ROIs for multiple classes, each class defined by a unique index and each ROI reported in a separate line.
     
For each image, `roi2bb` receives the path to the NIfTI image file, the path to the folder containing JSON files (one for each ROI) and the desired path to save the YOLO-compatible text file.

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
- nibabel (for handling NIfTI files)
- glob
- json
- argparse

## Installation

Simply download the `roi2bb` repository from the upper-right "Code" button dropdown menu, navigate to the roi2bb folder, organize your data to be compatible with the tool (see [Directory Structure](#directory-structure)) and define your desired class labels, like left_atrium, trachea, etc. (see ).

Here is a stepwise guide to use `roi2bb`:

### Directory Structure:

Following the YOLO input format, `roi2bb` converts the coordinates of multiple classes and multiple ROIs in each class, to a single text file. Hence, the only consideration is that each of the JSON folders must exclusively contain ROIs corresponding to a single image; Each JSon must be named after a predefined class label (e.g. left_atrium, trachea, etc.) and in case of multiple ROIs for one class, a number must be added by '_' (see below diagram). The numbering order and range do not matter.
Here is a sample structure, but you can use any structure for `roi2bb`'s Python API (see [Example usage](#usage)), as long as the JSON folder and files follow the mentioned rules.

```
project_directory/
├── images/
│   ├── Patient_001.nii or .nii.gz
│   ├── Patient_002.nii
│   │──...
├── labels/
│   ├── Patient_001/
│   │   ├── left_atrium.json
│   │   ├── lymph_node_4.json
│   │   ├── lymph_node_2.json
│   │   ├── lymph_node_3.json
│   │   └── trachea.json
│   ├── Patient_002/
│   │   ├── left_atrium.json
│   │   ├── lymph_node.json
│   │   └── trachea.json
│   │── ...
└── output/
    └── yolo_format.txt
```
### Class Index Mapping:

The method get_class_index maps ROI names to YOLO class indices. You can customize the class labels by editing the dictionary inside this method:

```bash
def get_class_index(self, class_label: str) -> int:
    class_mapping = {
        "left_atrium": 0,
        "lymph_node": 1,
        "trachea": 2,
        # Add more class labels and indices here
    }
    return class_mapping.get(class_label, -1)
```
### Example Usage:

Now that you downloaded the repository, organized your data and customized your labels, you can use the following commands in a command line interface (CLI) or the next one in a Python interface to convert ROIs to YOLO format by `roi2bb`:

**CLI**
```bash
python roi2bb.py path_to_image_file path_to_json_folder path_to_output_file
```
**Python API**
```bash
from roi2bb.converter import roi2bb

converter = roi2bb("path_to_image_file.nii", "path_to_json_folder", "output_yolo_format.txt")

converter.run()
```

### Example Output:
```bash
0 0.523 0.312 0.532 0.128 0.276 0.345  # left_atrium
1 0.734 0.512 0.723 0.132 0.254 0.367  # lymph_node_4
1 0.834 0.612 0.823 0.152 0.274 0.447  # lymph_node_2
2 0.634 0.412 0.623 0.112 0.234 0.287  # trachea
```
### License:

```roi2bb``` is released under the MIT License. See the [LICENSE](LICENSE) file for more details.

### Useful Links

[3D Slicer web page](https://www.slicer.org/) for volumetric medical imaging annotation

[Learn more about the coordinates systems](https://slicer.readthedocs.io/en/latest/user_guide/coordinate_systems.html)


### Contact:

Developer: Elham Mahmoudi

Email: mahmoudi.elham91@gmail.com

GitHub: [https://github.com/elimah91/roi2bb](https://github.com/elimah91/roi2bb)

