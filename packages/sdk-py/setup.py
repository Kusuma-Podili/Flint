from setuptools import setup, find_packages

setup(
    name="nexusops-sdk",
    version="1.0.0",
    description="Official Python SDK & CLI for NexusOps DevOps Automation Platform",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "pydantic>=2.5.0",
        "websockets>=12.0"
    ],
    entry_points={
        "console_scripts": [
            "nexusctl=nexusops.cli:main"
        ]
    }
)
