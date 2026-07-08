from __future__ import annotations

import json
import re
from pathlib import Path
from textwrap import dedent


ROOT = Path(__file__).resolve().parents[1]


TOPICS = [
    (
        "arrays-and-hashing",
        "Arrays & Hashing",
        "Use arrays, sets, and maps to track membership, counts, and complements.",
        [
            (1, "Contains Duplicate", 217, "Easy", "hasDuplicate"),
            (2, "Valid Anagram", 242, "Easy", "isAnagram"),
            (3, "Two Sum", 1, "Easy", "twoSum"),
            (4, "Group Anagrams", 49, "Medium", "groupAnagrams"),
            (5, "Top K Frequent Elements", 347, "Medium", "topKFrequent"),
            (6, "Encode and Decode Strings", 271, "Medium", "encode/decode"),
            (7, "Product of Array Except Self", 238, "Medium", "productExceptSelf"),
            (8, "Valid Sudoku", 36, "Medium", "isValidSudoku"),
            (9, "Longest Consecutive Sequence", 128, "Medium", "longestConsecutive"),
        ],
    ),
    (
        "two-pointers",
        "Two Pointers",
        "Move two indices with purpose to shrink, expand, or meet in the middle.",
        [
            (10, "Valid Palindrome", 125, "Easy", "isPalindrome"),
            (11, "Two Sum II", 167, "Medium", "twoSum"),
            (12, "3Sum", 15, "Medium", "threeSum"),
            (13, "Container With Most Water", 11, "Medium", "maxArea"),
            (14, "Trapping Rain Water", 42, "Hard", "trap"),
        ],
    ),
    (
        "sliding-window",
        "Sliding Window",
        "Maintain a moving range so repeated work is added and removed once.",
        [
            (15, "Best Time to Buy and Sell Stock", 121, "Easy", "maxProfit"),
            (16, "Longest Substring Without Repeating Characters", 3, "Medium", "lengthOfLongestSubstring"),
            (17, "Longest Repeating Character Replacement", 424, "Medium", "characterReplacement"),
            (18, "Permutation in String", 567, "Medium", "checkInclusion"),
            (19, "Minimum Window Substring", 76, "Hard", "minWindow"),
            (20, "Sliding Window Maximum", 239, "Hard", "maxSlidingWindow"),
        ],
    ),
    (
        "stack",
        "Stack",
        "Store unresolved items so the newest candidate can be handled first.",
        [
            (21, "Valid Parentheses", 20, "Easy", "isValid"),
            (22, "Min Stack", 155, "Medium", "MinStack"),
            (23, "Evaluate Reverse Polish Notation", 150, "Medium", "evalRPN"),
            (24, "Generate Parentheses", 22, "Medium", "generateParenthesis"),
            (25, "Daily Temperatures", 739, "Medium", "dailyTemperatures"),
            (26, "Car Fleet", 853, "Medium", "carFleet"),
            (27, "Largest Rectangle in Histogram", 84, "Hard", "largestRectangleArea"),
        ],
    ),
    (
        "binary-search",
        "Binary Search",
        "Cut a sorted search space in half, including answer spaces.",
        [
            (28, "Binary Search", 704, "Easy", "search"),
            (29, "Search a 2D Matrix", 74, "Medium", "searchMatrix"),
            (30, "Koko Eating Bananas", 875, "Medium", "minEatingSpeed"),
            (31, "Find Minimum in Rotated Sorted Array", 153, "Medium", "findMin"),
            (32, "Search in Rotated Sorted Array", 33, "Medium", "search"),
            (33, "Time Based Key-Value Store", 981, "Medium", "TimeMap"),
            (34, "Median of Two Sorted Arrays", 4, "Hard", "findMedianSortedArrays"),
        ],
    ),
    (
        "linked-list",
        "Linked List",
        "Manipulate node pointers while preserving the links you still need.",
        [
            (35, "Reverse Linked List", 206, "Easy", "reverseList"),
            (36, "Merge Two Sorted Lists", 21, "Easy", "mergeTwoLists"),
            (37, "Reorder List", 143, "Medium", "reorderList"),
            (38, "Remove Nth Node From End of List", 19, "Medium", "removeNthFromEnd"),
            (39, "Copy List With Random Pointer", 138, "Medium", "copyRandomList"),
            (40, "Add Two Numbers", 2, "Medium", "addTwoNumbers"),
            (41, "Linked List Cycle", 141, "Easy", "hasCycle"),
            (42, "Find the Duplicate Number", 287, "Medium", "findDuplicate"),
            (43, "LRU Cache", 146, "Medium", "LRUCache"),
            (44, "Merge K Sorted Lists", 23, "Hard", "mergeKLists"),
            (45, "Reverse Nodes in K-Group", 25, "Hard", "reverseKGroup"),
        ],
    ),
    (
        "trees",
        "Trees",
        "Use recursive structure, traversals, and subtree return values.",
        [
            (46, "Invert Binary Tree", 226, "Easy", "invertTree"),
            (47, "Maximum Depth of Binary Tree", 104, "Easy", "maxDepth"),
            (48, "Diameter of Binary Tree", 543, "Easy", "diameterOfBinaryTree"),
            (49, "Balanced Binary Tree", 110, "Easy", "isBalanced"),
            (50, "Same Tree", 100, "Easy", "isSameTree"),
            (51, "Subtree of Another Tree", 572, "Easy", "isSubtree"),
            (52, "Lowest Common Ancestor of a BST", 235, "Medium", "lowestCommonAncestor"),
            (53, "Binary Tree Level Order Traversal", 102, "Medium", "levelOrder"),
            (54, "Binary Tree Right Side View", 199, "Medium", "rightSideView"),
            (55, "Count Good Nodes in Binary Tree", 1448, "Medium", "goodNodes"),
            (56, "Validate Binary Search Tree", 98, "Medium", "isValidBST"),
            (57, "Kth Smallest Element in a BST", 230, "Medium", "kthSmallest"),
            (58, "Construct Binary Tree from Preorder and Inorder", 105, "Medium", "buildTree"),
            (59, "Binary Tree Maximum Path Sum", 124, "Hard", "maxPathSum"),
            (60, "Serialize and Deserialize Binary Tree", 297, "Hard", "Codec"),
        ],
    ),
    (
        "tries",
        "Tries",
        "Share prefixes across words to speed up lookup and search.",
        [
            (61, "Implement Trie (Prefix Tree)", 208, "Medium", "Trie"),
            (62, "Design Add and Search Words Data Structure", 211, "Medium", "WordDictionary"),
            (63, "Word Search II", 212, "Hard", "findWords"),
        ],
    ),
    (
        "heap-priority-queue",
        "Heap / Priority Queue",
        "Keep the next best or next smallest item available in logarithmic time.",
        [
            (64, "Kth Largest Element in a Stream", 703, "Easy", "KthLargest"),
            (65, "Last Stone Weight", 1046, "Easy", "lastStoneWeight"),
            (66, "K Closest Points to Origin", 973, "Medium", "kClosest"),
            (67, "Kth Largest Element in an Array", 215, "Medium", "findKthLargest"),
            (68, "Task Scheduler", 621, "Medium", "leastInterval"),
            (69, "Design Twitter", 355, "Medium", "Twitter"),
            (70, "Find Median From Data Stream", 295, "Hard", "MedianFinder"),
        ],
    ),
    (
        "backtracking",
        "Backtracking",
        "Build candidates depth-first and undo choices when a branch is done.",
        [
            (71, "Subsets", 78, "Medium", "subsets"),
            (72, "Combination Sum", 39, "Medium", "combinationSum"),
            (73, "Permutations", 46, "Medium", "permute"),
            (74, "Subsets II", 90, "Medium", "subsetsWithDup"),
            (75, "Combination Sum II", 40, "Medium", "combinationSum2"),
            (76, "Word Search", 79, "Medium", "exist"),
            (77, "Palindrome Partitioning", 131, "Medium", "partition"),
            (78, "Letter Combinations of a Phone Number", 17, "Medium", "letterCombinations"),
            (79, "N-Queens", 51, "Hard", "solveNQueens"),
        ],
    ),
    (
        "graphs",
        "Graphs",
        "Traverse nodes and edges while tracking visited state and components.",
        [
            (80, "Number of Islands", 200, "Medium", "numIslands"),
            (81, "Max Area of Island", 695, "Medium", "maxAreaOfIsland"),
            (82, "Clone Graph", 133, "Medium", "cloneGraph"),
            (83, "Walls and Gates", 286, "Medium", "wallsAndGates"),
            (84, "Rotting Oranges", 994, "Medium", "orangesRotting"),
            (85, "Pacific Atlantic Water Flow", 417, "Medium", "pacificAtlantic"),
            (86, "Surrounded Regions", 130, "Medium", "solve"),
            (87, "Course Schedule", 207, "Medium", "canFinish"),
            (88, "Course Schedule II", 210, "Medium", "findOrder"),
            (89, "Graph Valid Tree", 261, "Medium", "validTree"),
            (90, "Number of Connected Components in an Undirected Graph", 323, "Medium", "countComponents"),
            (91, "Redundant Connection", 684, "Medium", "findRedundantConnection"),
            (92, "Word Ladder", 127, "Hard", "ladderLength"),
        ],
    ),
    (
        "advanced-graphs",
        "Advanced Graphs",
        "Combine graph traversal with heaps, ordering, and shortest-path ideas.",
        [
            (93, "Reconstruct Itinerary", 332, "Hard", "findItinerary"),
            (94, "Min Cost to Connect All Points", 1584, "Medium", "minCostConnectPoints"),
            (95, "Network Delay Time", 743, "Medium", "networkDelayTime"),
            (96, "Swim in Rising Water", 778, "Hard", "swimInWater"),
            (97, "Alien Dictionary", 269, "Hard", "foreignDictionary"),
            (98, "Cheapest Flights Within K Stops", 787, "Medium", "findCheapestPrice"),
        ],
    ),
    (
        "1-d-dynamic-programming",
        "1-D Dynamic Programming",
        "Cache the best answer for each position or amount in one dimension.",
        [
            (99, "Climbing Stairs", 70, "Easy", "climbStairs"),
            (100, "Min Cost Climbing Stairs", 746, "Easy", "minCostClimbingStairs"),
            (101, "House Robber", 198, "Medium", "rob"),
            (102, "House Robber II", 213, "Medium", "rob"),
            (103, "Longest Palindromic Substring", 5, "Medium", "longestPalindrome"),
            (104, "Palindromic Substrings", 647, "Medium", "countSubstrings"),
            (105, "Decode Ways", 91, "Medium", "numDecodings"),
            (106, "Coin Change", 322, "Medium", "coinChange"),
            (107, "Maximum Product Subarray", 152, "Medium", "maxProduct"),
            (108, "Word Break", 139, "Medium", "wordBreak"),
            (109, "Longest Increasing Subsequence", 300, "Medium", "lengthOfLIS"),
            (110, "Partition Equal Subset Sum", 416, "Medium", "canPartition"),
        ],
    ),
    (
        "2-d-dynamic-programming",
        "2-D Dynamic Programming",
        "Cache subproblem answers over two changing coordinates or ranges.",
        [
            (111, "Unique Paths", 62, "Medium", "uniquePaths"),
            (112, "Longest Common Subsequence", 1143, "Medium", "longestCommonSubsequence"),
            (113, "Best Time to Buy and Sell Stock With Cooldown", 309, "Medium", "maxProfit"),
            (114, "Coin Change II", 518, "Medium", "change"),
            (115, "Target Sum", 494, "Medium", "findTargetSumWays"),
            (116, "Interleaving String", 97, "Medium", "isInterleave"),
            (117, "Longest Increasing Path in a Matrix", 329, "Hard", "longestIncreasingPath"),
            (118, "Distinct Subsequences", 115, "Hard", "numDistinct"),
            (119, "Edit Distance", 72, "Medium", "minDistance"),
            (120, "Burst Balloons", 312, "Hard", "maxCoins"),
            (121, "Regular Expression Matching", 10, "Hard", "isMatch"),
        ],
    ),
    (
        "greedy",
        "Greedy",
        "Make the locally useful choice when an invariant proves it is safe.",
        [
            (122, "Maximum Subarray", 53, "Medium", "maxSubArray"),
            (123, "Jump Game", 55, "Medium", "canJump"),
            (124, "Jump Game II", 45, "Medium", "jump"),
            (125, "Gas Station", 134, "Medium", "canCompleteCircuit"),
            (126, "Hand of Straights", 846, "Medium", "isNStraightHand"),
            (127, "Merge Triplets to Form Target Triplet", 1899, "Medium", "mergeTriplets"),
            (128, "Partition Labels", 763, "Medium", "partitionLabels"),
            (129, "Valid Parenthesis String", 678, "Medium", "checkValidString"),
        ],
    ),
    (
        "intervals",
        "Intervals",
        "Sort ranges and reason about overlaps, starts, and ends.",
        [
            (130, "Insert Interval", 57, "Medium", "insert"),
            (131, "Merge Intervals", 56, "Medium", "merge"),
            (132, "Non-Overlapping Intervals", 435, "Medium", "eraseOverlapIntervals"),
            (133, "Meeting Rooms", 252, "Easy", "canAttendMeetings"),
            (134, "Meeting Rooms II", 253, "Medium", "minMeetingRooms"),
            (135, "Minimum Interval to Include Each Query", 1851, "Hard", "minInterval"),
        ],
    ),
    (
        "math-and-geometry",
        "Math & Geometry",
        "Translate the problem into arithmetic, coordinates, or matrix movement.",
        [
            (136, "Rotate Image", 48, "Medium", "rotate"),
            (137, "Spiral Matrix", 54, "Medium", "spiralOrder"),
            (138, "Set Matrix Zeroes", 73, "Medium", "setZeroes"),
            (139, "Happy Number", 202, "Easy", "isHappy"),
            (140, "Plus One", 66, "Easy", "plusOne"),
            (141, "Pow(x, n)", 50, "Medium", "myPow"),
            (142, "Multiply Strings", 43, "Medium", "multiply"),
            (143, "Detect Squares", 2013, "Medium", "DetectSquares"),
        ],
    ),
    (
        "bit-manipulation",
        "Bit Manipulation",
        "Use binary representation to isolate, combine, or count bits.",
        [
            (144, "Single Number", 136, "Easy", "singleNumber"),
            (145, "Number of 1 Bits", 191, "Easy", "hammingWeight"),
            (146, "Counting Bits", 338, "Easy", "countBits"),
            (147, "Reverse Bits", 190, "Easy", "reverseBits"),
            (148, "Missing Number", 268, "Easy", "missingNumber"),
            (149, "Sum of Two Integers", 371, "Medium", "getSum"),
            (150, "Reverse Integer", 7, "Medium", "reverse"),
        ],
    ),
]


URL_OVERRIDES = {
    "Two Sum II": "two-sum-ii-input-array-is-sorted",
    "3Sum": "3sum",
    "Kth Largest Element in a Stream": "kth-largest-element-in-a-stream",
    "Time Based Key-Value Store": "time-based-key-value-store",
    "Implement Trie (Prefix Tree)": "implement-trie-prefix-tree",
    "Design Add and Search Words Data Structure": "design-add-and-search-words-data-structure",
    "1-D Dynamic Programming": "1-d-dynamic-programming",
    "Pow(x, n)": "powx-n",
}

DESIGN_CLASSES = {
    "MinStack",
    "TimeMap",
    "LRUCache",
    "Codec",
    "Trie",
    "WordDictionary",
    "KthLargest",
    "Twitter",
    "MedianFinder",
    "DetectSquares",
}


def slugify(value: str) -> str:
    value = value.lower()
    value = value.replace("&", "and")
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value


def leetcode_url(title: str) -> str:
    return f"https://leetcode.com/problems/{URL_OVERRIDES.get(title, slugify(title))}/"


def starter_for(method: str) -> str:
    if method == "encode/decode":
        return dedent(
            """
            from __future__ import annotations


            class Solution:
                def encode(self, strs: list[str]) -> str:
                    # Your code here
                    pass

                def decode(self, s: str) -> list[str]:
                    # Your code here
                    pass
            """
        ).lstrip()
    if method in DESIGN_CLASSES:
        return dedent(
            f"""
            from __future__ import annotations


            class {method}:
                def __init__(self, *args):
                    # See LeetCode for the full design interface.
                    pass
            """
        ).lstrip()
    return dedent(
        f"""
        from __future__ import annotations


        class Solution:
            def {method}(self, *args, **kwargs):
                # Your code here
                pass
        """
    ).lstrip()


def base_problem(pid, title, lc, difficulty, method, topic_name, topic_slug, seeded, local_index):
    slug = slugify(title)
    runner = {"entry": "method", "method": method, "compare": "exact", "timeout_sec": 10}
    if method == "encode/decode":
        runner = {"entry": "roundtrip", "encode": "encode", "decode": "decode", "compare": "exact", "timeout_sec": 10}
    elif method in DESIGN_CLASSES:
        runner = {"entry": "design", "class": method, "compare": "exact", "timeout_sec": 10}
    return {
        "id": pid,
        "slug": slug,
        "title": title,
        "difficulty": difficulty,
        "topic": topic_name,
        "topic_slug": topic_slug,
        "leetcode": lc,
        "leetcode_url": leetcode_url(title),
        "neetcode_url": None,
        "pattern": topic_name,
        "seeded": seeded,
        "runner": runner,
        "statement": f"{title} is not seeded yet. Use the LeetCode link for the full prompt, then practice locally with the starter signature.",
        "examples": [],
        "constraints": [],
        "hints": [],
        "cases": [],
    }


VALID_BOARD = [
    list("53..7...."),
    list("6..195..."),
    list(".98....6."),
    list("8...6...3"),
    list("4..8.3..1"),
    list("7...2...6"),
    list(".6....28."),
    list("...419..5"),
    list("....8..79"),
]
INVALID_BOARD = [
    list("83..7...."),
    list("6..195..."),
    list(".98....6."),
    list("8...6...3"),
    list("4..8.3..1"),
    list("7...2...6"),
    list(".6....28."),
    list("...419..5"),
    list("....8..79"),
]


SEEDED = {
    1: {
        "pattern": "Duplicate detection with a set",
        "runner": {"entry": "method", "method": "hasDuplicate", "compare": "bool", "timeout_sec": 3},
        "statement": "Given a list of integers, return true when at least one value appears more than once. Return false when every value is unique.",
        "examples": [
            {"input": "nums = [1,2,3,1]", "output": "true"},
            {"input": "nums = [1,2,3,4]", "output": "false"},
        ],
        "constraints": ["The input is a list of integers.", "A linear-time solution should use extra space for seen values."],
        "hints": ["A duplicate means a value was seen earlier.", "A set gives constant-time membership checks.", "Return as soon as a repeated value is found."],
        "cases": [
            {"kind": "example", "args": {"nums": [1, 2, 3, 1]}, "expected": True},
            {"kind": "example", "args": {"nums": [1, 2, 3, 4]}, "expected": False},
            {"kind": "edge", "note": "single item", "args": {"nums": [7]}, "expected": False},
            {"kind": "edge", "note": "negative duplicate", "args": {"nums": [-1, 4, -1]}, "expected": True},
            {"kind": "stress", "note": "large list with duplicate at end", "gen": {"fn": "make_case", "seed": 1}, "timeout_sec": 3},
        ],
        "fixtures": "def make_case(seed):\n    nums = list(range(20000)) + [19999]\n    return {'args': {'nums': nums}, 'expected': True}\n",
        "reference": "class Solution:\n    def hasDuplicate(self, nums):\n        return len(nums) != len(set(nums))\n",
    },
    2: {
        "pattern": "Character counting",
        "runner": {"entry": "method", "method": "isAnagram", "compare": "bool", "timeout_sec": 3},
        "statement": "Given two strings, return true when they contain the same characters with the same counts, regardless of order.",
        "examples": [
            {"input": "s = \"anagram\", t = \"nagaram\"", "output": "true"},
            {"input": "s = \"rat\", t = \"car\"", "output": "false"},
        ],
        "constraints": ["Inputs are strings.", "A count-based solution should run in linear time."],
        "hints": ["Anagrams must have the same length.", "Count how many times each character appears.", "The two count maps must match exactly."],
        "cases": [
            {"kind": "example", "args": {"s": "anagram", "t": "nagaram"}, "expected": True},
            {"kind": "example", "args": {"s": "rat", "t": "car"}, "expected": False},
            {"kind": "edge", "note": "empty strings", "args": {"s": "", "t": ""}, "expected": True},
            {"kind": "edge", "note": "same letters different counts", "args": {"s": "aacc", "t": "ccac"}, "expected": False},
            {"kind": "stress", "gen": {"fn": "make_case", "seed": 1}, "timeout_sec": 3},
        ],
        "fixtures": "def make_case(seed):\n    s = 'abcxyz' * 10000\n    return {'args': {'s': s, 't': ''.join(reversed(s))}, 'expected': True}\n",
        "reference": "from collections import Counter\n\nclass Solution:\n    def isAnagram(self, s, t):\n        return Counter(s) == Counter(t)\n",
    },
    3: {
        "pattern": "Hash map complement lookup",
        "runner": {"entry": "method", "method": "twoSum", "compare": "sorted", "timeout_sec": 5},
        "statement": "Given an array of integers nums and an integer target, return the indices of the two numbers that add up to target. Assume exactly one valid pair exists, and you may not reuse the same element.",
        "examples": [
            {"input": "nums = [2,7,11,15], target = 9", "output": "[0,1]", "explanation": "nums[0] + nums[1] = 9."},
            {"input": "nums = [3,2,4], target = 6", "output": "[1,2]"},
        ],
        "constraints": ["2 <= nums.length <= 100000", "Exactly one valid answer exists.", "Return zero-based indices."],
        "hints": ["Brute force checks every pair.", "Store values you have already passed.", "Look up target - current before inserting current."],
        "cases": [
            {"kind": "example", "args": {"nums": [2, 7, 11, 15], "target": 9}, "expected": [0, 1]},
            {"kind": "example", "args": {"nums": [3, 2, 4], "target": 6}, "expected": [1, 2]},
            {"kind": "edge", "note": "duplicate values", "args": {"nums": [3, 3], "target": 6}, "expected": [0, 1]},
            {"kind": "edge", "note": "negatives sum to zero", "args": {"nums": [-3, 4, 3, 90], "target": 0}, "expected": [0, 2]},
            {"kind": "stress", "note": "pair at the end", "gen": {"fn": "make_case", "seed": 1}, "timeout_sec": 2},
        ],
        "fixtures": "def make_case(seed):\n    nums = list(range(100000))\n    return {'args': {'nums': nums, 'target': 199997}, 'expected': [99998, 99999]}\n",
        "reference": "class Solution:\n    def twoSum(self, nums, target):\n        seen = {}\n        for i, n in enumerate(nums):\n            if target - n in seen:\n                return [seen[target - n], i]\n            seen[n] = i\n        return []\n",
    },
    4: {
        "pattern": "Group by normalized key",
        "runner": {"entry": "method", "method": "groupAnagrams", "compare": "groups", "timeout_sec": 5},
        "statement": "Given a list of strings, group together words that are anagrams of one another. The order of groups and words inside each group does not matter.",
        "examples": [{"input": "strs = [\"eat\",\"tea\",\"tan\",\"ate\",\"nat\",\"bat\"]", "output": "[[\"bat\"],[\"nat\",\"tan\"],[\"ate\",\"eat\",\"tea\"]]"}],
        "constraints": ["Strings may be empty.", "A sorted word or character-count tuple can identify each group."],
        "hints": ["Anagrams share the same letters.", "Turn each word into a canonical key.", "Append the original word to the bucket for that key."],
        "cases": [
            {"kind": "example", "args": {"strs": ["eat", "tea", "tan", "ate", "nat", "bat"]}, "expected": [["eat", "tea", "ate"], ["tan", "nat"], ["bat"]]},
            {"kind": "edge", "args": {"strs": [""]}, "expected": [[""]]},
            {"kind": "edge", "args": {"strs": ["a"]}, "expected": [["a"]]},
            {"kind": "stress", "gen": {"fn": "make_case", "seed": 1}, "timeout_sec": 5},
        ],
        "fixtures": "def make_case(seed):\n    words = ['abc', 'bca', 'cab', 'foo', 'ofo', 'bar'] * 1000\n    return {'args': {'strs': words}, 'expected': [['abc', 'bca', 'cab'] * 1000, ['foo', 'ofo'] * 1000, ['bar'] * 1000]}\n",
        "reference": "from collections import defaultdict\n\nclass Solution:\n    def groupAnagrams(self, strs):\n        groups = defaultdict(list)\n        for word in strs:\n            groups[''.join(sorted(word))].append(word)\n        return list(groups.values())\n",
    },
    5: {
        "pattern": "Frequency counting",
        "runner": {"entry": "method", "method": "topKFrequent", "compare": "sorted", "timeout_sec": 5},
        "statement": "Return the k values that appear most often in the input list. The answer can be returned in any order.",
        "examples": [{"input": "nums = [1,1,1,2,2,3], k = 2", "output": "[1,2]"}],
        "constraints": ["1 <= k <= number of distinct values.", "The output order does not matter."],
        "hints": ["Count each number first.", "You only need the k largest counts.", "A heap or bucket list avoids sorting everything for large inputs."],
        "cases": [
            {"kind": "example", "args": {"nums": [1, 1, 1, 2, 2, 3], "k": 2}, "expected": [1, 2]},
            {"kind": "edge", "args": {"nums": [1], "k": 1}, "expected": [1]},
            {"kind": "edge", "args": {"nums": [-1, -1, 2, 2, 2, 3], "k": 2}, "expected": [-1, 2]},
            {"kind": "stress", "gen": {"fn": "make_case", "seed": 1}, "timeout_sec": 5},
        ],
        "fixtures": "def make_case(seed):\n    nums = []\n    for value in range(30):\n        nums.extend([value] * (30 - value))\n    return {'args': {'nums': nums, 'k': 5}, 'expected': [0, 1, 2, 3, 4]}\n",
        "reference": "from collections import Counter\n\nclass Solution:\n    def topKFrequent(self, nums, k):\n        return [num for num, count in Counter(nums).most_common(k)]\n",
    },
    6: {
        "pattern": "Length-prefixed serialization",
        "runner": {"entry": "roundtrip", "encode": "encode", "decode": "decode", "compare": "exact", "timeout_sec": 5},
        "statement": "Design a pair of methods that turns a list of strings into one string and back again, preserving empty strings and delimiter characters.",
        "examples": [{"input": "strs = [\"neet\",\"co#de\",\"\"]", "output": "[\"neet\",\"co#de\",\"\"]"}],
        "constraints": ["Strings may contain punctuation or digits.", "The encoded format must be unambiguous."],
        "hints": ["Joining on a delimiter breaks when the delimiter appears in data.", "Store each string length before its contents.", "During decode, read the length, skip the separator, then slice that many characters."],
        "cases": [
            {"kind": "example", "args": {"strs": ["neet", "co#de", ""]}, "expected": ["neet", "co#de", ""]},
            {"kind": "edge", "args": {"strs": []}, "expected": []},
            {"kind": "edge", "args": {"strs": ["#", "12#abc", ""]}, "expected": ["#", "12#abc", ""]},
            {"kind": "stress", "gen": {"fn": "make_case", "seed": 1}, "timeout_sec": 5},
        ],
        "fixtures": "def make_case(seed):\n    strs = [str(i) + '#value' for i in range(2000)]\n    return {'args': {'strs': strs}, 'expected': strs}\n",
        "reference": "class Solution:\n    def encode(self, strs):\n        return ''.join(f'{len(s)}#{s}' for s in strs)\n\n    def decode(self, s):\n        out = []\n        i = 0\n        while i < len(s):\n            j = s.index('#', i)\n            size = int(s[i:j])\n            start = j + 1\n            out.append(s[start:start + size])\n            i = start + size\n        return out\n",
    },
    7: {
        "pattern": "Prefix and suffix products",
        "runner": {"entry": "method", "method": "productExceptSelf", "compare": "exact", "timeout_sec": 5},
        "statement": "Return an array where each position contains the product of every input value except the one at that same position, without using division.",
        "examples": [{"input": "nums = [1,2,3,4]", "output": "[24,12,8,6]"}],
        "constraints": ["Do not use division.", "Zeros must be handled naturally."],
        "hints": ["The answer at i is product to the left times product to the right.", "Build prefix products in one pass.", "Multiply by suffix products in a reverse pass."],
        "cases": [
            {"kind": "example", "args": {"nums": [1, 2, 3, 4]}, "expected": [24, 12, 8, 6]},
            {"kind": "example", "args": {"nums": [-1, 1, 0, -3, 3]}, "expected": [0, 0, 9, 0, 0]},
            {"kind": "edge", "args": {"nums": [0, 0]}, "expected": [0, 0]},
            {"kind": "stress", "gen": {"fn": "make_case", "seed": 1}, "timeout_sec": 5},
        ],
        "fixtures": "def make_case(seed):\n    nums = [1] * 20000\n    return {'args': {'nums': nums}, 'expected': nums[:]}\n",
        "reference": "class Solution:\n    def productExceptSelf(self, nums):\n        out = [1] * len(nums)\n        prefix = 1\n        for i, n in enumerate(nums):\n            out[i] = prefix\n            prefix *= n\n        suffix = 1\n        for i in range(len(nums) - 1, -1, -1):\n            out[i] *= suffix\n            suffix *= nums[i]\n        return out\n",
    },
    8: {
        "pattern": "Row column and box sets",
        "runner": {"entry": "method", "method": "isValidSudoku", "compare": "bool", "timeout_sec": 5},
        "statement": "Return true if a partially filled 9 by 9 Sudoku board has no repeated digit in any row, column, or 3 by 3 box. Dots are empty cells.",
        "examples": [{"input": "board = standard partially-filled valid board", "output": "true"}],
        "constraints": ["The board has 9 rows and 9 columns.", "Only digits 1-9 and dots appear."],
        "hints": ["Each filled cell belongs to one row, one column, and one box.", "Track seen digits for all three scopes.", "A repeated digit in any scope makes the board invalid."],
        "cases": [
            {"kind": "example", "args": {"board": VALID_BOARD}, "expected": True},
            {"kind": "edge", "note": "duplicate in box", "args": {"board": INVALID_BOARD}, "expected": False},
            {"kind": "stress", "args": {"board": VALID_BOARD}, "expected": True, "timeout_sec": 5},
        ],
        "reference": "class Solution:\n    def isValidSudoku(self, board):\n        rows, cols, boxes = [set() for _ in range(9)], [set() for _ in range(9)], [set() for _ in range(9)]\n        for r in range(9):\n            for c in range(9):\n                value = board[r][c]\n                if value == '.':\n                    continue\n                b = (r // 3) * 3 + c // 3\n                if value in rows[r] or value in cols[c] or value in boxes[b]:\n                    return False\n                rows[r].add(value); cols[c].add(value); boxes[b].add(value)\n        return True\n",
    },
    9: {
        "pattern": "Set starts of runs",
        "runner": {"entry": "method", "method": "longestConsecutive", "compare": "exact", "timeout_sec": 5},
        "statement": "Given unsorted integers, return the length of the longest run of consecutive values.",
        "examples": [{"input": "nums = [100,4,200,1,3,2]", "output": "4"}],
        "constraints": ["The input may be empty.", "A set-based solution should run in linear time."],
        "hints": ["Only begin counting at the start of a run.", "A number starts a run when number - 1 is absent.", "Walk forward while the next value exists."],
        "cases": [
            {"kind": "example", "args": {"nums": [100, 4, 200, 1, 3, 2]}, "expected": 4},
            {"kind": "example", "args": {"nums": [0, 3, 7, 2, 5, 8, 4, 6, 0, 1]}, "expected": 9},
            {"kind": "edge", "args": {"nums": []}, "expected": 0},
            {"kind": "edge", "args": {"nums": [1, 2, 0, 1]}, "expected": 3},
            {"kind": "stress", "gen": {"fn": "make_case", "seed": 1}, "timeout_sec": 5},
        ],
        "fixtures": "def make_case(seed):\n    nums = list(range(50000))\n    return {'args': {'nums': nums}, 'expected': 50000}\n",
        "reference": "class Solution:\n    def longestConsecutive(self, nums):\n        values = set(nums)\n        best = 0\n        for n in values:\n            if n - 1 not in values:\n                cur = n\n                while cur in values:\n                    cur += 1\n                best = max(best, cur - n)\n        return best\n",
    },
    10: {
        "pattern": "Filtered two-pointer scan",
        "runner": {"entry": "method", "method": "isPalindrome", "compare": "bool", "timeout_sec": 5},
        "statement": "Return true when a string reads the same forward and backward after ignoring non-alphanumeric characters and letter case.",
        "examples": [{"input": "s = \"A man, a plan, a canal: Panama\"", "output": "true"}],
        "constraints": ["Ignore punctuation and spaces.", "Compare letters without case sensitivity."],
        "hints": ["Move one pointer from each end.", "Skip characters that are not letters or digits.", "Compare lowercased characters when both pointers are valid."],
        "cases": [
            {"kind": "example", "args": {"s": "A man, a plan, a canal: Panama"}, "expected": True},
            {"kind": "example", "args": {"s": "race a car"}, "expected": False},
            {"kind": "edge", "args": {"s": " "}, "expected": True},
            {"kind": "edge", "args": {"s": "0P"}, "expected": False},
            {"kind": "stress", "gen": {"fn": "make_case", "seed": 1}, "timeout_sec": 5},
        ],
        "fixtures": "def make_case(seed):\n    half = 'abc123' * 10000\n    s = half + '!!!' + half[::-1]\n    return {'args': {'s': s}, 'expected': True}\n",
        "reference": "class Solution:\n    def isPalindrome(self, s):\n        left, right = 0, len(s) - 1\n        while left < right:\n            while left < right and not s[left].isalnum():\n                left += 1\n            while left < right and not s[right].isalnum():\n                right -= 1\n            if s[left].lower() != s[right].lower():\n                return False\n            left += 1; right -= 1\n        return True\n",
    },
    11: {
        "pattern": "Two pointers on sorted input",
        "runner": {"entry": "method", "method": "twoSum", "compare": "exact", "timeout_sec": 5},
        "statement": "Given a sorted list of integers and a target, return the one-based positions of the two values that add to the target.",
        "examples": [{"input": "numbers = [2,7,11,15], target = 9", "output": "[1,2]"}],
        "constraints": ["The input is sorted in nondecreasing order.", "Exactly one valid answer exists.", "Return one-based indices."],
        "hints": ["Use the sorted order.", "If the sum is too small, move the left pointer right.", "If the sum is too large, move the right pointer left."],
        "cases": [
            {"kind": "example", "args": {"numbers": [2, 7, 11, 15], "target": 9}, "expected": [1, 2]},
            {"kind": "edge", "args": {"numbers": [2, 3, 4], "target": 6}, "expected": [1, 3]},
            {"kind": "edge", "args": {"numbers": [-1, 0], "target": -1}, "expected": [1, 2]},
            {"kind": "stress", "gen": {"fn": "make_case", "seed": 1}, "timeout_sec": 5},
        ],
        "fixtures": "def make_case(seed):\n    numbers = list(range(1, 100001))\n    return {'args': {'numbers': numbers, 'target': 199999}, 'expected': [99999, 100000]}\n",
        "reference": "class Solution:\n    def twoSum(self, numbers, target):\n        left, right = 0, len(numbers) - 1\n        while left < right:\n            total = numbers[left] + numbers[right]\n            if total == target:\n                return [left + 1, right + 1]\n            if total < target:\n                left += 1\n            else:\n                right -= 1\n        return []\n",
    },
    12: {
        "pattern": "Sorted scan with duplicate skipping",
        "runner": {"entry": "method", "method": "threeSum", "compare": "groups", "timeout_sec": 8},
        "statement": "Return every unique triplet of numbers that sums to zero. Each triplet may be in any order, and the list of triplets may be in any order.",
        "examples": [{"input": "nums = [-1,0,1,2,-1,-4]", "output": "[[-1,-1,2],[-1,0,1]]"}],
        "constraints": ["The answer must not contain duplicate triplets.", "Sorting lets the inner search use two pointers."],
        "hints": ["Sort the numbers first.", "Fix one value and use two pointers for the remaining sum.", "Skip duplicate fixed values and duplicate pointer values."],
        "cases": [
            {"kind": "example", "args": {"nums": [-1, 0, 1, 2, -1, -4]}, "expected": [[-1, -1, 2], [-1, 0, 1]]},
            {"kind": "edge", "args": {"nums": [0, 1, 1]}, "expected": []},
            {"kind": "edge", "args": {"nums": [0, 0, 0]}, "expected": [[0, 0, 0]]},
            {"kind": "edge", "args": {"nums": [0, 0, 0, 0]}, "expected": [[0, 0, 0]]},
            {"kind": "stress", "gen": {"fn": "make_case", "seed": 1}, "timeout_sec": 8},
        ],
        "fixtures": "def _three_sum(nums):\n    nums = sorted(nums)\n    out = []\n    for i, n in enumerate(nums):\n        if i and n == nums[i - 1]:\n            continue\n        left, right = i + 1, len(nums) - 1\n        while left < right:\n            total = n + nums[left] + nums[right]\n            if total == 0:\n                out.append([n, nums[left], nums[right]])\n                left += 1; right -= 1\n                while left < right and nums[left] == nums[left - 1]: left += 1\n                while left < right and nums[right] == nums[right + 1]: right -= 1\n            elif total < 0:\n                left += 1\n            else:\n                right -= 1\n    return out\n\ndef make_case(seed):\n    nums = list(range(-120, 121)) + list(range(-60, 61))\n    return {'args': {'nums': nums}, 'expected': _three_sum(nums)}\n",
        "reference": "class Solution:\n    def threeSum(self, nums):\n        nums.sort()\n        out = []\n        for i, n in enumerate(nums):\n            if i > 0 and n == nums[i - 1]:\n                continue\n            left, right = i + 1, len(nums) - 1\n            while left < right:\n                total = n + nums[left] + nums[right]\n                if total == 0:\n                    out.append([n, nums[left], nums[right]])\n                    left += 1; right -= 1\n                    while left < right and nums[left] == nums[left - 1]:\n                        left += 1\n                    while left < right and nums[right] == nums[right + 1]:\n                        right -= 1\n                elif total < 0:\n                    left += 1\n                else:\n                    right -= 1\n        return out\n",
    },
    13: {
        "pattern": "Opposing pointers maximize area",
        "runner": {"entry": "method", "method": "maxArea", "compare": "exact", "timeout_sec": 5},
        "statement": "Given vertical line heights, choose two lines that hold the most water with the x-axis. Return the maximum area.",
        "examples": [{"input": "height = [1,8,6,2,5,4,8,3,7]", "output": "49"}],
        "constraints": ["Area is width times the shorter height.", "Moving the shorter side is the useful greedy step."],
        "hints": ["Start at both ends.", "The smaller height limits the current area.", "Move the pointer at the smaller height inward."],
        "cases": [
            {"kind": "example", "args": {"height": [1, 8, 6, 2, 5, 4, 8, 3, 7]}, "expected": 49},
            {"kind": "edge", "args": {"height": [1, 1]}, "expected": 1},
            {"kind": "edge", "args": {"height": [4, 3, 2, 1, 4]}, "expected": 16},
            {"kind": "edge", "args": {"height": [1, 2, 1]}, "expected": 2},
            {"kind": "stress", "gen": {"fn": "make_case", "seed": 1}, "timeout_sec": 5},
        ],
        "fixtures": "def make_case(seed):\n    height = list(range(1, 5000))\n    left, right = 0, len(height) - 1\n    best = 0\n    while left < right:\n        best = max(best, (right - left) * min(height[left], height[right]))\n        if height[left] < height[right]: left += 1\n        else: right -= 1\n    return {'args': {'height': height}, 'expected': best}\n",
        "reference": "class Solution:\n    def maxArea(self, height):\n        left, right = 0, len(height) - 1\n        best = 0\n        while left < right:\n            best = max(best, (right - left) * min(height[left], height[right]))\n            if height[left] < height[right]:\n                left += 1\n            else:\n                right -= 1\n        return best\n",
    },
    14: {
        "pattern": "Two-sided water boundary",
        "runner": {"entry": "method", "method": "trap", "compare": "exact", "timeout_sec": 5},
        "statement": "Given bar heights, compute how much rain water is trapped after raining.",
        "examples": [{"input": "height = [0,1,0,2,1,0,1,3,2,1,2,1]", "output": "6"}],
        "constraints": ["Water above a bar is limited by the lower max wall on either side.", "A two-pointer solution can track both side maximums."],
        "hints": ["Keep pointers at both ends.", "Track the tallest wall seen from each side.", "The side with the lower current maximum determines trapped water there."],
        "cases": [
            {"kind": "example", "args": {"height": [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]}, "expected": 6},
            {"kind": "example", "args": {"height": [4, 2, 0, 3, 2, 5]}, "expected": 9},
            {"kind": "edge", "args": {"height": []}, "expected": 0},
            {"kind": "edge", "args": {"height": [2, 0, 2]}, "expected": 2},
            {"kind": "stress", "gen": {"fn": "make_case", "seed": 1}, "timeout_sec": 5},
        ],
        "fixtures": "def make_case(seed):\n    height = [5] + [0] * 5000 + [5]\n    return {'args': {'height': height}, 'expected': 25000}\n",
        "reference": "class Solution:\n    def trap(self, height):\n        if not height:\n            return 0\n        left, right = 0, len(height) - 1\n        left_max = right_max = 0\n        water = 0\n        while left < right:\n            if height[left] < height[right]:\n                left_max = max(left_max, height[left])\n                water += left_max - height[left]\n                left += 1\n            else:\n                right_max = max(right_max, height[right])\n                water += right_max - height[right]\n                right -= 1\n        return water\n",
    },
}


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def problem_readme(problem: dict) -> str:
    examples = "\n".join(f"- Input: `{ex['input']}`; Output: `{ex['output']}`" for ex in problem.get("examples", []))
    constraints = "\n".join(f"- {item}" for item in problem.get("constraints", []))
    return dedent(
        f"""
        # {problem['title']}

        {problem['statement']}

        LeetCode: {problem['leetcode_url']}

        ## Examples
        {examples or '- Not seeded yet.'}

        ## Constraints
        {constraints or '- See the linked problem.'}
        """
    ).lstrip()


def main() -> None:
    roadmap = {"version": 1, "language": "python", "source": "NeetCode 150", "topics": []}
    for topic_index, (topic_slug, topic_name, blurb, problems) in enumerate(TOPICS, start=1):
        topic_dir = f"problems/{topic_index:02d}-{topic_slug}"
        topic_entry = {"id": topic_index, "slug": topic_slug, "name": topic_name, "blurb": blurb, "problems": []}
        for local_index, (pid, title, lc, difficulty, method) in enumerate(problems, start=1):
            seeded = pid in SEEDED
            problem = base_problem(pid, title, lc, difficulty, method, topic_name, topic_slug, seeded, local_index)
            if seeded:
                problem.update({k: v for k, v in SEEDED[pid].items() if k not in {"reference", "fixtures"}})
                problem["seeded"] = True
            problem_slug = problem["slug"]
            pdir = Path(topic_dir) / f"{local_index:02d}-{problem_slug}"
            problem["dir"] = str(pdir)
            topic_entry["problems"].append(
                {
                    "id": pid,
                    "slug": problem_slug,
                    "title": title,
                    "difficulty": difficulty,
                    "leetcode": lc,
                    "leetcode_url": problem["leetcode_url"],
                    "method": None if method in DESIGN_CLASSES else method,
                    "seeded": seeded,
                    "dir": str(pdir),
                }
            )

            abs_dir = ROOT / pdir
            abs_dir.mkdir(parents=True, exist_ok=True)
            write(abs_dir / "problem.json", json.dumps(problem, indent=2, sort_keys=True) + "\n")
            write(abs_dir / "README.md", problem_readme(problem))
            write(abs_dir / "starter.py", starter_for(method))
            if seeded:
                write(abs_dir / "reference.py", SEEDED[pid]["reference"])
                if "fixtures" in SEEDED[pid]:
                    write(abs_dir / "fixtures.py", SEEDED[pid]["fixtures"])
            else:
                write(abs_dir / "reference.py", "# Not seeded yet.\n")

        roadmap["topics"].append(topic_entry)

    write(ROOT / "roadmap.json", json.dumps(roadmap, indent=2, sort_keys=True) + "\n")
    write(
        ROOT / "_template" / "problem.json",
        json.dumps(
            {
                "id": 0,
                "slug": "new-problem",
                "title": "New Problem",
                "difficulty": "Medium",
                "topic": "Topic",
                "topic_slug": "topic",
                "leetcode": 0,
                "leetcode_url": "",
                "neetcode_url": None,
                "pattern": "",
                "seeded": False,
                "runner": {"entry": "method", "method": "solve", "compare": "exact", "timeout_sec": 10},
                "statement": "",
                "examples": [],
                "constraints": [],
                "hints": [],
                "cases": [],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
    )
    write(ROOT / "_template" / "starter.py", starter_for("solve"))
    write(ROOT / "_template" / "reference.py", "# Add a reference solution when seeded.\n")


if __name__ == "__main__":
    main()
