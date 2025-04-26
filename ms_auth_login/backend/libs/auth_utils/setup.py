# File: backend/libs/auth_utils/setup.py
from setuptools import setup, find_namespace_packages

setup(
    name="auth_utils",
    version="0.1.0",
    packages=find_namespace_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "pyjwt",
        "fastapi",
        "pydantic",
        "cryptography"
    ],
)