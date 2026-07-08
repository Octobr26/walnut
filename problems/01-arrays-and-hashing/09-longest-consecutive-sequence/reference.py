class Solution:
    def longestConsecutive(self, nums):
        values = set(nums)
        best = 0
        for n in values:
            if n - 1 not in values:
                cur = n
                while cur in values:
                    cur += 1
                best = max(best, cur - n)
        return best
