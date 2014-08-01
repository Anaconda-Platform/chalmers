'''
Created on Jun 24, 2014

@author: sean
'''
from chalmers import errors
import shlex

def make_definition(data):
    if 'name' not in data:
        raise errors.ChalmersError("Program definition is missing the field 'name'" % data)

    if 'command' not in data:
        raise errors.ChalmersError("Program definition %(name)s is missing the field 'command'" % data)

    if 'groups' in data:
        if isinstance(data['groups'], str):
            data['groups'] = [data['groups']]

    if isinstance(data['command'], str):
        data['command'] = shlex.split(data['command'])


    if not isinstance(data['command'], list):
        raise errors.ChalmersError("The field 'command' must be a list or a string got %r" % type(data['command']))

    return data


