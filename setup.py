from setuptools import find_packages, setup

setup(
    name="dagster-example",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "dagster>=1.5.0",
        "dagster-webserver>=1.5.0",
        "duckdb>=0.9.0",
        "pandas>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "dagster-test>=1.5.0",
        ],
    },
)
