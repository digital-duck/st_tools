# Creating a Python Package for Local Installation

## 1. Set up your package structure

First, create this basic directory structure:

```
utils-u8hi/
├── utils_u8hi/
│   ├── __init__.py
│   ├── helper_api.py
│   └── helper_agno.py
├── setup.py
├── README.md
└── LICENSE
```

## 2. Create the `__init__.py` file

In the inner `my_package/__init__.py`, add imports for any functions you want to make available when someone imports your package:

```python
# my_package/__init__.py
from .module1 import some_function
from .module2 import another_function

__version__ = '0.1.0'
```

## 3. Create your module files

Add your actual code to the module files:

```python
# my_package/module1.py
def some_function():
    return "Hello from module1!"
```

## 4. Create `setup.py`

This is the most important file for package installation:

```python
from setuptools import setup, find_packages

setup(
    name="my_package",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        # List your dependencies here
        # "requests>=2.25.1",
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="A short description of your package",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/my_package",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
```

## 5. Install your package locally

You have three main options for local installation:

### Option 1: Development mode
This creates a link to your source code (changes to your code will be reflected immediately):

```bash
cd /path/to/my_package
pip install -e .
```

### Option 2: Build and install
Build a distributable package and install it:

```bash
cd /path/to/my_package
pip install .
```

### Option 3: Build distribution files
Create distribution files that can be shared:

```bash
cd /path/to/my_package
python -m build
pip install dist/my_package-0.1.0-py3-none-any.whl
```
(You'll need to `pip install build` first for this option)

## 6. Test your installation

Create a new Python file outside your package directory:

```python
# test_import.py
import my_package

print(my_package.some_function())
```

## References

- https://claude.ai/chat/95e40f6a-9053-4c45-acfa-90f856dc633a