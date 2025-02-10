from setuptools import setup, find_packages

setup(
    name="roi2bb",
    version="0.1.0",
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
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "roi2bb=roi2bb.converter:main"
        ],
    },
)

