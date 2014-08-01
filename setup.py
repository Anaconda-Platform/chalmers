'''
@author: sean
'''

from setuptools import setup, find_packages

setup(
    name='Chalmers',
    version="dev",
    author='Sean Ross-Ross',
    author_email='srossross@gmail.com',
    url='http://github.com/srossross/chalmers',
    packages=find_packages(),
    entry_points={
          'console_scripts': [
              'chalmers = chalmers.scripts.chalmers_main:main',
              'chalmers-runner = chalmers.scripts.chalmers_runner:main',
              ]
                 },
)

