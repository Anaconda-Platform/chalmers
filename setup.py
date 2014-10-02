from setuptools import setup, find_packages
import os

install_requires = ['psutil', 'clyent']

if os.name == 'nt':
    install_requires.append('pywin32')

setup(
    name='chalmers',
    version="0.1.4",
    author='Continuum Analytics',
    author_email='srossross@gmail.com',
    url='http://github.com/binstar/chalmers',
    packages=find_packages(),
    install_requires=install_requires,
    entry_points={
          'console_scripts': [
              'chalmers = chalmers.scripts.chalmers_main:main',
              ]
                 },
)

