from setuptools import setup, find_packages

setup(
    name="utils_u8hi",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        # List your dependencies here
        # "requests>=2.25.1",
    ],
    author="Digital Duck",
    author_email="p2p2learn@outlook.com",
    description="Helper package to get API key securely, log Agno agent message",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/digital-duck/st_tools",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)