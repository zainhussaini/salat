import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="salat",
    version="0.1.0",
    description="Tool to calculate accurate salat (prayer) times",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/zainhussaini/salat",
    author="Zain Hussaini",
    author_email="zih301@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
    packages=["salat"],
    include_package_data=True,
    install_requires=[],
)
