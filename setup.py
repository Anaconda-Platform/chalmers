from setuptools import setup, find_packages
import os
import versioneer

install_requires = ['psutil>=2.1.3', 'clyent', 'pyyaml']

if os.name == 'nt':
    install_requires.append('pywin32')


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
       'chalmers.service': ['data/*'],
    },

    entry_points={
          'console_scripts': [
              'chalmers = chalmers.scripts.chalmers_main:main',
              ]
                 },
)

