from chalmers import errors
import shlex

def make_definition(data):
    """
    Turn the 'data' dict into a standard definition 
    """
    if 'name' not in data:
        raise errors.ChalmersError("Program definition is missing the field 'name'" % data)

    if 'command' not in data:
        raise errors.ChalmersError("Program definition %(name)s is missing the field 'command'" % data)

    if 'extends' in data:
        if isinstance(data['extends'], str):
            data['extends'] = [data['extends']]

    if isinstance(data['command'], str):
        data['command'] = shlex.split(data['command'])


    if not isinstance(data['command'], list):
        raise errors.ChalmersError("The field 'command' must be a list or a string got %r" % type(data['command']))

    return data


