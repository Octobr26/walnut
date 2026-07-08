def make_case(seed):
    strs = [str(i) + '#value' for i in range(2000)]
    return {'args': {'strs': strs}, 'expected': strs}
