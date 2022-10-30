import codecs

from setuptools import find_packages, setup

with codecs.open("README_ENG.md", "r", encoding='utf-8') as readme_file:
    readme = readme_file.read()

setup(
    name='pyBrNews',
    packages=find_packages(),
    install_requires=[
        "loguru>=0.6.0", "pymongo>=4.3.2", "requests_html>=0.10.0"
    ],
    version='0.1.2',
    description='A Brazilian News Website Data Acquisition Library for Python',
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://www.github.com/NepZR/pyBrNews/",
    author='Lucas Darlindo Freitas Rodrigues',
    author_email="lucas.darlindo@gmail.com",
    license='GNU GPLv3',
    license_files=(
        'LICENSE',
    ),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Framework :: IPython",
        "Framework :: Jupyter",
        "Framework :: Jupyter :: JupyterLab",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Natural Language :: Portuguese (Brazilian)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Database",
        "Topic :: Education",
        "Topic :: Internet",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Version Control :: Git",
        "Topic :: Text Processing",
        "Topic :: Text Processing :: Markup :: HTML",
        "Topic :: Text Processing :: Markup :: XML"
    ]
)
