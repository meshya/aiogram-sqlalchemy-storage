from setuptools import setup, find_packages

setup(
    name="aiogram-sqlalchemy-storage",
    version='v0.2.0-0',
    description="SQLAlchemy-based storage for aiogram FSM",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="meshya",
    author_email="meshmeshmeshya@gmail.com",
    url="https://github.com/meshya/aiogram-sqlalchemy-storage",
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
