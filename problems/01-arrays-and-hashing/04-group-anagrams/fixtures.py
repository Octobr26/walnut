def make_case(seed):
    words = ['abc', 'bca', 'cab', 'foo', 'ofo', 'bar'] * 1000
    return {'args': {'strs': words}, 'expected': [['abc', 'bca', 'cab'] * 1000, ['foo', 'ofo'] * 1000, ['bar'] * 1000]}
