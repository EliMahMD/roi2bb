from setuptools import setup, find_packages

setup(
    name='roi2bb', 
    version='0.1.0', 
    description='A tool to convert coordinates of 3D Slicer JSON annotations to YOLO format.', 
    url='https://github.com/elimah91/ROI2BB', 
    author='Elham Mahmoudi',  
    author_email='mahmoudi.elham91@gmail.com', 
    license='MIT',  
    packages=find_packages(), 
    classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    ],
    install_requires=[  
        json,
        nibabel or pydicom or PIL,
        os,
        glob,
        argparse,
    ],
    entry_points={ 
        'console_scripts': [
            'roi2bb=roi2bb:main', 
        ],
    },
)

