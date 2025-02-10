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
    install_requires=[
        "numpy",
        "pandas",
        "opencv-python",
        "pydicom",
        "nibabel",
        "Pillow",
        "SimpleITK"
    ],
    python_requires=">=3.7"
    classifiers=[
        "Programming Language :: Python :: 3.x",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "roi2bb=roi2bb.converter:main"
        ],
    },
)
