# ROI2BB
# ROI to YOLO Bounding Box Converter

This repository provides a Python class, ROI2BB, for converting Regions of Interest (ROI) stored in 3D Slicer JSON format into bounding box coordinates in YOLO format. These two coordinate systems have 3 main differnces that should be addressed while converting:

1. The Slicer output follows the "Patient coordinate system", which its origin is located at an anatomical landmark not necessarily in the image boundaries, while the YOLO-compatible input format is based on "Image coordinate system", which its origin is located at upper-left corner of the image. Also, the axis directions are not the same in differnet coordinate systems, changing the point coordinate values.
    
2. The Slicer format dimensions are the actual ROI dimensions, while theYolo format dimensions are a ratio of ROI dimension to image dimensions. 

3. The Slicer output is in Json format with the ROI 'center' coordinates (x,y,z) and ROI dimensions 'size' (x_length, y_length,z_length) reported under 'markups' tag, while YOLO-compatible input is a text file with each line presenting one ROI containing: 
    "class cneter_z center_x center_y z_length x_length y_length"
     
For each image, ROI2BB receives the path to the NIfTI image file, the path to the folder containing Json files (one for each ROI) and the desired path to save the YOLO-compatible text file.

The expected data structure is:

# images
    # Patient_001.nii
    # Patient_002.nii
    # ...
# labels
    # Patient_001
    #     left_atrium.mrk.json
    #     right_atrium.mrk.json
    #     ...
    # Patient_002
    #     left_atrium.mrk.json
    #     right_atrium.mrk.json
    #     ...
    # ...
