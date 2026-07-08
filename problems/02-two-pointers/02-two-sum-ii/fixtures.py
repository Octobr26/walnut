def make_case(seed):
    numbers = list(range(1, 100001))
    return {'args': {'numbers': numbers, 'target': 199999}, 'expected': [99999, 100000]}
