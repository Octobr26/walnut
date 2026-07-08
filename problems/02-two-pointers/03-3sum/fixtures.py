def _three_sum(nums):
    nums = sorted(nums)
    out = []
    for i, n in enumerate(nums):
        if i and n == nums[i - 1]:
            continue
        left, right = i + 1, len(nums) - 1
        while left < right:
            total = n + nums[left] + nums[right]
            if total == 0:
                out.append([n, nums[left], nums[right]])
                left += 1; right -= 1
                while left < right and nums[left] == nums[left - 1]: left += 1
                while left < right and nums[right] == nums[right + 1]: right -= 1
            elif total < 0:
                left += 1
            else:
                right -= 1
    return out

def make_case(seed):
    nums = list(range(-120, 121)) + list(range(-60, 61))
    return {'args': {'nums': nums}, 'expected': _three_sum(nums)}
