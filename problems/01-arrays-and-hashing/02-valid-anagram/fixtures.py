def make_case(seed):
    s = 'abcxyz' * 10000
    return {'args': {'s': s, 't': ''.join(reversed(s))}, 'expected': True}
