def make_case(seed):
    nums = list(range(100000))
    return {'args': {'nums': nums, 'target': 199997}, 'expected': [99998, 99999]}
