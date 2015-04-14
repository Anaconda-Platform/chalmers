from setuptools import setup, find_packages
import os

install_requires = ['psutil>=2.1.3', 'clyent', 'pyyaml']

if os.name == 'nt':
    install_requires.append('pywin32')


import versioneer
versioneer.VCS = 'git'
versioneer.versionfile_source = 'chalmers/_version.py'
versioneer.versionfile_build = 'chalmers/_version.py'
versioneer.tag_prefix = ''  # tags are like 1.2.0
versioneer.parentdir_prefix = 'chalmers-'  # dirname like 'myproject-1.2.0'


setup(
    name='chalmers',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author='Continuum Analytics',
    author_email='srossross@gmail.com',
    url='http://github.com/binstar/chalmers',
    description='Process Control System',
    packages=find_packages(),
    install_requires=install_requires,
    package_data={
       'chlamers.service': ['data/*'],
    },

    entry_points={
          'console_scripts': [
              'chalmers = chalmers.scripts.chalmers_main:main',
              ]
                 },
)

