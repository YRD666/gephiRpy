from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="gephi-cli",
    version="2.0.0",
    description="Python interface to Gephi graph analysis toolkit - CLI + Python API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="yangr",
    url="https://github.com/yangr/gephi-cli",
    packages=find_packages(),
    install_requires=[
        "jpype1>=1.5.0",
        "click>=8.1.0",
        "rich>=13.0.0",
        "pyyaml>=6.0",
    ],
    extras_require={
        "networkx": ["networkx>=3.0"],
        "pandas": ["pandas>=2.0"],
        "numpy": ["numpy>=1.24"],
        "all": ["networkx>=3.0", "pandas>=2.0", "numpy>=1.24"],
    },
    entry_points={
        "console_scripts": [
            "gephi-cli=gephi_cli.cli:main",
        ],
    },
    python_requires=">=3.10",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    package_data={
        "gephi_cli": [],
    },
    include_package_data=True,
)
