# 2-D Dynamic Programming

## The grid shapes

```python
# unique paths / min path sum: dp[r][c] from top and left
dp = [[0] * n for _ in range(m)]           # NEVER [[0]*n]*m (row aliasing)
# rolling 1-D row:
row = [1] * n
for r in range(1, m):
    for c in range(1, n):
        row[c] += row[c - 1]
```

## Two-sequence DP (the big family)
State: `dp[i][j]` = answer for `s1[:i]` vs `s2[:j]`. Size (m+1) x (n+1), row/col 0 = empty prefix.

```python
# longest common subsequence
dp = [[0] * (n + 1) for _ in range(m + 1)]
for i in range(1, m + 1):
    for j in range(1, n + 1):
        if s1[i - 1] == s2[j - 1]:
            dp[i][j] = dp[i - 1][j - 1] + 1
        else:
            dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

# edit distance: match -> diag; else 1 + min(insert, delete, replace)
#   dp[i][j] = dp[i-1][j-1] if eq else 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])
#   base: dp[i][0] = i, dp[0][j] = j

# distinct subsequences: dp[i][j] = dp[i-1][j] (+ dp[i-1][j-1] if chars match)

# interleaving string: dp[i][j] = (dp[i-1][j] and s1[i-1]==s3[i+j-1]) or (dp[i][j-1] and ...)
```

## Knapsack shapes

```python
# 0/1 knapsack (target sum, partition): iterate items, sums DESCENDING
dp = [False] * (target + 1); dp[0] = True
for x in nums:
    for s in range(target, x - 1, -1):     # descending = each item used once
        dp[s] = dp[s] or dp[s - x]

# unbounded (coin change II — count ways): coins OUTER, sums ascending
dp = [1] + [0] * amount
for c in coins:
    for s in range(c, amount + 1):
        dp[s] += dp[s - c]
```

## Interval DP (burst balloons)
`dp[l][r]` = best for open interval (l, r); pick LAST balloon k to pop:
`dp[l][r] = max(nums[l]*nums[k]*nums[r] + dp[l][k] + dp[k][r])`. Iterate by interval length. O(n^3).

## Stock problems with state machine
State = (day, holding, transactions_left / cooldown). Write transitions, memoize:
`hold = max(hold, prev_free - price)`, `free = max(free, hold + price)`; cooldown delays `free` by a day.

## Gotchas
- Direction of iteration IS the algorithm in knapsack: descending = 0/1, ascending = unbounded.
- Index offset: `dp[i][j]` pairs with `s[i-1]`, `t[j-1]`. Off-by-one capital of DP.
- Memoized top-down with `@lru_cache` on `(i, j)` is often fastest to write correctly under pressure.
