from setuptools import find_packages, setup

setup(
    name='pyBrNews',
    packages=find_packages(
        include=["News", "Comments", "config"]
    ),
    install_requires=[
        "loguru>=0.6.0", "pymongo>=4.3.2", "requests_html>=0.10.0"
    ],
    version='0.1.0',
    description='A Brazilian News Website Data Acquisition Library for Python',
    author='Lucas Darlindo Freitas Rodrigues',
    license='GNU GPLv3',
)
