from setuptools import setup, find_packages

setup(
    name="mapsampler",
    version="0.1",
    license="GPL3",
    description="Mapping based nucleotide sequence filtering",
    package_dir={"": "src"},  # Packages are inside 'src/'
    packages=find_packages(where="src"),  # Finds packages inside 'src/'
    install_requires=["psutil"],
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "mapsampler=mapsampler.ms:main",  # Correct format
        ],
    },
)