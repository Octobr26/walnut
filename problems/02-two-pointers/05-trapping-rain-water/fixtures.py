def make_case(seed):
    height = [5] + [0] * 5000 + [5]
    return {'args': {'height': height}, 'expected': 25000}
