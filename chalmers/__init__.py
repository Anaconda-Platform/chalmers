
try:
    from _version import __version__
except ImportError:
    __version__ = '0.3'


from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
