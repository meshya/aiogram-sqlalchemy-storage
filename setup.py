from setuptools import setup, find_packages

import subprocess

def get_version():
    try:
        return subprocess.check_output(["git", "describe", "--tags", "--always"]).strip().decode()
    except Exception:
        return "0.1.0"

setup(
    name="aiogram-sqlalchemy-storage",
    version=get_version(),
    description="SQLAlchemy-based storage for aiogram FSM",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/aiogram-sqlalchemy-storage",
    packages=find_packages(),
    install_requires=[
        "aiogram>=3",
        "SQLAlchemy>=2",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
)
