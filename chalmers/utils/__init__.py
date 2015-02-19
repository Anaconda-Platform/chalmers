'''
'''
from __future__ import print_function, unicode_literals
from yaml import safe_load
import logging
from pprint import pformat


log = logging.getLogger(__name__)

def try_eval(value):
    "Try and evaluate a literal value, if it fails, return a string"
    try:
        return safe_load(value)
    except:
        return value

def set_nested_key(dct, key, value):
    """
    Set a nested key in a dictionary
    """

    keys = key.split('.')
    next_key = keys.pop(0)

    while keys:
        dct = dct.setdefault(next_key, {})
        next_key = keys.pop(0)

    dct[next_key] = value
    pass

def pformat2(value):
    pvalue = pformat(value, width=66).split('\n')
    sep = '\n' + ' ' * 14
    return sep.join(pvalue)


def print_opts(category, data, opts, file=None):
    'Print all options from dict "data" that are in "category"'
    if not any(opt in data for opt in opts):
        return
    print('\n%s' % category, file=file)
    print('-' * len(category), file=file)
    for opt in opts:
        if opt in data:
            value = data.get(opt)
            print("%12s: %s" % (opt, pformat2(value)), file=file)
