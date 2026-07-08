class Solution:
    def productExceptSelf(self, nums):
        out = [1] * len(nums)
        prefix = 1
        for i, n in enumerate(nums):
            out[i] = prefix
            prefix *= n
        suffix = 1
        for i in range(len(nums) - 1, -1, -1):
            out[i] *= suffix
            suffix *= nums[i]
        return out
