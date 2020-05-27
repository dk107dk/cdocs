import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cdocs",
    version="0.0.9",
    author="David Kershaw",
    author_email="dk107dk@hotmail.com",
    description="Cdocs is a super simple contextual help library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dk107dk/cdocs",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
