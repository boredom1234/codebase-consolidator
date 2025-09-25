#!/usr/bin/env python3

from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="codebase-consolidator",
    version="1.0.0",
    author="Codebase Consolidator",
    author_email="your.email@example.com",
    description="A CLI tool to consolidate entire codebases into organized markdown files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/boredom1234/codebase-consolidator",
    py_modules=["codebase_consolidator", "codebase_consolidator_gui"],
    install_requires=[
        "ttkbootstrap>=1.10.1",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Documentation",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "codebase-consolidator=codebase_consolidator:main",
            "cc=codebase_consolidator:main",
        ],
        "gui_scripts": [
            "codebase-consolidator-gui=codebase_consolidator_gui:main",
            "cc-gui=codebase_consolidator_gui:main",
        ],
    },
    keywords="codebase consolidate markdown documentation development tools cli",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/codebase-consolidator/issues",
        "Source": "https://github.com/yourusername/codebase-consolidator",
    },
)
