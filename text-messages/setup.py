import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="text-message-analyzer-dhruvpillai6", # Replace with your own username
    version="0.0.1",
    author="Dhruv Pillai",
    author_email="dhruvpillai6@gmail.com",
    description="A package for helping develop insight into patterns that exist in "
                "your text messages for Mac users.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        # "License :: OSI Approved :: MIT License",
        # "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)