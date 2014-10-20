from setuptools import setup, find_packages
import os

install_requires = ['psutil', 'clyent', 'pyyaml']

if os.name == 'nt':
    install_requires.append('pywin32')


ctx = {}
try:
    with open('chalmers/_version.py') as fd:
        exec(open('chalmers/_version.py').read(), ctx)
    version = ctx.get('__version__', 'dev')
except IOError:
    version = 'dev'

setup(
    name='chalmers',
    version=version,
    author='Continuum Analytics',
    author_email='srossross@gmail.com',
    url='http://github.com/binstar/chalmers',
    description='Process Control System',
    packages=find_packages(),
    install_requires=install_requires,
    entry_points={
          'console_scripts': [
              'chalmers = chalmers.scripts.chalmers_main:main',
              ]
                 },
)

