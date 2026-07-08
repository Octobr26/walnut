from collections import Counter

class Solution:
    def topKFrequent(self, nums, k):
        return [num for num, count in Counter(nums).most_common(k)]
