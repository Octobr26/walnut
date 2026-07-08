def make_case(seed):
    half = 'abc123' * 10000
    s = half + '!!!' + half[::-1]
    return {'args': {'s': s}, 'expected': True}
