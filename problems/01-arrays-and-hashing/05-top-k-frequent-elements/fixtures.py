def make_case(seed):
    nums = []
    for value in range(30):
        nums.extend([value] * (30 - value))
    return {'args': {'nums': nums, 'k': 5}, 'expected': [0, 1, 2, 3, 4]}
