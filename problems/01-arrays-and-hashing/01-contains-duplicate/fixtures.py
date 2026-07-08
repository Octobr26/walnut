def make_case(seed):
    nums = list(range(20000)) + [19999]
    return {'args': {'nums': nums}, 'expected': True}
