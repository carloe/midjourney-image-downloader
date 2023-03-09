import os
from setuptools import setup, find_packages
from io import open

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

if not os.path.isdir("jobs"):
    os.makedirs("jobs")

setup(
    name='midjourney-image-downloader',
    version='0.0.1',
    packages=find_packages(),
    url='',
    license='MIT',
    author='nicky',
    author_email='nicky.reid92@gmail.com',
    description='Download images from your Midjourney gallery',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=[
        "requests",
        "click",
    ],
    entry_points={
        'console_scripts': [
            'mjdl=src.__main__:cli',
        ],
    },
)
