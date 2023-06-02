from setuptools import setup, find_packages

with open("./README.md", "r+", encoding='utf-8') as readme_file:
    readme = readme_file.read()

requirements = ["aiogram>2"]

setup(
    name="aiogram-customizable-paginator",
    version="0.1.0",
    author="BathrosT",
    author_email="bathris12@gmail.com",
    description="Python library that provides functionality for paging through a list of objects. It allows you to easily navigate through the list using inline buttons",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/BathrisT/aiogram-customizable-paginator",
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[],
)