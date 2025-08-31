from setuptools import setup, find_packages

setup(
    name="billo",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "toga-android>=0.5.2",
        "python-dotenv>=1.0.0",
        "segno>=1.5.0",
        "aiohttp>=3.9.0"
    ],
    python_requires=">=3.10",
)
