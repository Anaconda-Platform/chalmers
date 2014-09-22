'''
@author: sean
'''

from setuptools import setup, find_packages
# from distutils.core import setup

setup(
    name='Chalmers',
    version="dev",
    author='Sean Ross-Ross',
    author_email='srossross@gmail.com',
    url='http://github.com/srossross/chalmers',
    packages=['chalmers'],
    entry_points={
          'console_scripts': [
              'chalmers = chalmers.scripts.chalmers_main:main',
              'chalmers-runner = chalmers.scripts.chalmers_runner:main',
              ]
                 },
)

