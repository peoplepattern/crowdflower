def rails(value, prefix=''):
    if isinstance(value, list):
        for subvalue in value:
            for pair in rails(subvalue, prefix=prefix + '[]'):
                yield pair
    elif isinstance(value, dict):
        for subkey, subvalue in value.items():
            for pair in rails(subvalue, prefix=prefix + '[' + subkey + ']'):
                yield pair
    else:
        yield prefix, value


def rails_params(params):
    for root, value in params.items():
        for pair in rails(value, prefix=root):
            yield pair
