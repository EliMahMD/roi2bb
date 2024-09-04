from setuptools import setup, find_packages

setup(
    name='roi2bb',  # Your package name
    version='0.1.0',  # The initial release version
    description='Convert ROIs from 3D Slicer JSON format to YOLO bounding boxes',  # Short description of your package
    long_description=open('README.md').read(),  # You can use your README as a long description
    long_description_content_type='text/markdown',  # This is important if you're using Markdown for the long description
    url='https://github.com/elimah91/ROI2BB',  # The URL of your project's homepage or repository
    author='Your Name',  # Your name
    author_email='your.email@example.com',  # Your email address
    license='MIT',  # License under which your code is distributed
    packages=find_packages(),  # Automatically find packages in your project
    install_requires=[  # External packages that your project depends on
        'nibabel',
        'json',
        'numpy',
        'glob'
    ],
    python_requires='>=3.6',  # Specify Python versions that are supported
    entry_points={  # Optional: If you're adding command-line scripts
        'console_scripts': [
            'roi2bb=roi2bb:main',  # Creates a command line script `roi2bb` that calls your `main()` function
        ],
    },
)

