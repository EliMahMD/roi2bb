import json
import nibabel as nib
import os
import glob
import argparse


class roi2bb:
    def __init__(self, image_file_path: str, json_folder_path: str, output_file_path: str):
        self.image_file_path = image_file_path # required for the calculation of Yolo format bbox dimensions since the YOLO bbox dimensions are a ratio of original image's dimensions
        self.json_folder_path = json_folder_path # path to the folder containing 3D Slicer's output JSON files for all ROIs of a single image
        self.output_file_path = output_file_path # the output text file containing the YOLO format coordinates of all ROIs per image
        self.yolo_content = [] #output text file content
        
        self.img = nib.load(image_file_path)
        self.header = self.img.header
        self.image_resolution = self.header.get_zooms()
        self.image_physical_size_mm = [self.header.get_data_shape()[i] * self.image_resolution[i] for i in range(3)]
        self.topleft = self.img.affine[:3, 3] #New origin in the Image coordinate system
        
        # Correct axis direction discordances in the two coordinate systems
        self.topleft[1] = -1 * self.topleft[1] 
        self.topleft[2] = -1 * self.topleft[2]
        
    def convert_single_roi(self, json_file_path: str):
        base_class_label = os.path.basename(json_file_path).split('.')[0] # extract the class label from the json file name
        if base_class_label.rsplit('_', 1)[-1].isdigit(): #in case of multiple ROIs per class
            print('number detected')
            base_class_label = base_class_label.rsplit('_', 1)[0]
            
        with open(json_file_path, 'r') as file: 
            json_data = file.read()
        data = json.loads(json_data) # extract the Slicer format coordinates and dimensions from the Json files
        
        roi = data['markups'][0]
        center = roi['center']
        roi_size_mm = roi['size']
        
        # Correct axis directions
        center[0] = -1 * center[0]
        center[2] = -1 * center[2]
        new_center = [self.topleft[i] - center[i] for i in range(3)]

        # Calculate the ROI center coordinates and dimensions from the new origin (YOLO format)
        yolo_center = [new_center[i] / self.image_physical_size_mm[i] for i in range(3)]
        yolo_size = [
            roi_size_mm[0] / self.image_physical_size_mm[0],
            roi_size_mm[1] / self.image_physical_size_mm[1],
            roi_size_mm[2] / self.image_physical_size_mm[2]
        ]
        
        class_index = self.get_class_index(base_class_label)
        yolo_format = f"{class_index} {yolo_center[2]} {yolo_center[0]} {yolo_center[1]} {yolo_size[2]} {yolo_size[0]} {yolo_size[1]}"
        # Add multiple ROIs of a single image to output a single text file containing each ROI as a separate line
        self.yolo_content.append(yolo_format)

    def get_class_index(self, class_label: str) -> int:
        # Define a mapping between class labels and class indices (customize this as needed)
        class_mapping = {
            "left_atrium": 0,
            "trachea": 1,
            "lymph_node": 2,
            # Add more class labels and indices here
        }
        return class_mapping.get(class_label, -1)  # Return -1 if class not found
    
    def process_all_rois(self):
        json_file_list = glob.glob(os.path.join(self.json_folder_path, '*.json'))
        for json_file_path in json_file_list:
            self.convert_single_roi(json_file_path)
    
    def save_output(self):
        with open(self.output_file_path, 'w') as file:
            file.write("\n".join(self.yolo_content))

    def run(self):
        self.process_all_rois()
        self.save_output()

def main():
    parser = argparse.ArgumentParser(description='Convert 3D Slicer ROIs to YOLO bounding box format.')
    parser.add_argument('image_file', type=str, help='Path to the input NIfTI image file (.nii or .nii.gz).')
    parser.add_argument('json_folder', type=str, help='Path to the folder containing the 3D Slicer ROI JSON files.')
    parser.add_argument('output_file', type=str, help='Path to the output YOLO format text file.')
    
    args = parser.parse_args()
    
    # Initialize the roi2bb converter
    converter = roi2bb(args.image_file, args.json_folder, args.output_file)
    
    # Run the conversion process
    converter.run()
    print(f'Converted ROIs from {args.json_folder} and saved YOLO format output to {args.output_file}')


if __name__ == '__main__':
    main()
