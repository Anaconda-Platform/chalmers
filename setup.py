from setuptools import setup
import os

install_requires = ['psutil']

if os.name == 'nt':
    install_requires.append('pywin32')

setup(
    name='Chalmers',
    version="dev",
    author='Sean Ross-Ross',
    author_email='srossross@gmail.com',
    url='http://github.com/srossross/chalmers',
    packages=['chalmers'],
    install_requires=install_requires,
    entry_points={
          'console_scripts': [
              'chalmers = chalmers.scripts.chalmers_main:main',
              'chalmers-runner = chalmers.scripts.chalmers_runner:main',
              ]
                 },
)

