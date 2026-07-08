# 1-D Dynamic Programming

## Method (every time)
1. Define state in words: `dp[i] = best answer for prefix/suffix ending at i`.
2. Recurrence: how does `dp[i]` come from earlier states?
3. Base cases. 4. Order (usually left→right). 5. Roll variables if only last k states used.

## Core recurrences

```python
# climbing stairs / fibonacci: dp[i] = dp[i-1] + dp[i-2]
a, b = 1, 1
for _ in range(n - 1):
    a, b = b, a + b

# house robber: rob or skip
rob, skip = 0, 0
for x in nums:
    rob, skip = skip + x, max(rob, skip)
ans = max(rob, skip)
# robber II (circle): max(rob(nums[1:]), rob(nums[:-1]))

# coin change (min coins) — unbounded knapsack shape
dp = [0] + [math.inf] * amount
for a in range(1, amount + 1):
    for c in coins:
        if c <= a:
            dp[a] = min(dp[a], dp[a - c] + 1)

# word break
dp = [True] + [False] * n
for i in range(1, n + 1):
    dp[i] = any(dp[j] and s[j:i] in words for j in range(i))

# longest increasing subsequence
dp = [1] * n                                  # O(n^2)
for i in range(n):
    for j in range(i):
        if nums[j] < nums[i]:
            dp[i] = max(dp[i], dp[j] + 1)
# O(n log n): tails list + bisect_left, replace or append

# max subarray (Kadane)
cur = best = nums[0]
for x in nums[1:]:
    cur = max(x, cur + x)
    best = max(best, cur)
# max PRODUCT: track (curmax, curmin), negatives swap them

# decode ways: dp[i] += dp[i-1] if s[i-1] != '0'; += dp[i-2] if 10 <= int(s[i-2:i]) <= 26

# partition equal subset sum: set of reachable sums
reach = {0}
for x in nums:
    reach |= {s + x for s in reach}
return target in reach

# palindromic substrings / longest palindrome: expand around center
for center in range(n):
    expand(center, center); expand(center, center + 1)   # odd + even
```

## Top-down alternative
`@lru_cache(maxsize=None)` on `def dp(i):` — same recurrence, Python writes the table. Fine unless depth > ~1000.

## Gotchas
- Coin change order: `for amount: for coins` counts combinations of min-coins fine; for COUNT-of-ways problems, loop coins OUTER to avoid counting permutations.
- Kadane with all-negatives: init with `nums[0]`, not 0.
- LIS `bisect_left` on tails gives length, not the sequence itself.
