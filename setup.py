import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="graph-network-HUYNH-THANH-QUAN",
    version="0.1.0",
    author="Huynh Thanh Quan",
    author_email="hthquan28@gmail.com",
    description="A library to help visualize graph network, integrate with some utility functions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/HuynhThanhQuan/graph-network",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='3.6',
)
