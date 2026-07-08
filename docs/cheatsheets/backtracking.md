# Backtracking

## Skeleton (everything here is this shape)

```python
def backtrack(state, choices):
    if goal(state):
        res.append(state.copy())        # COPY — state mutates after
        return
    for choice in choices:
        if not valid(choice): continue  # prune
        state.append(choice)            # choose
        backtrack(...)                  # explore
        state.pop()                     # un-choose
```

## The classic variants

```python
# subsets: at each index, include or skip
def dfs(i, path):
    if i == len(nums):
        res.append(path.copy()); return
    path.append(nums[i]); dfs(i + 1, path); path.pop()   # include
    dfs(i + 1, path)                                     # skip
# or iterate: for j in range(i, n): append, dfs(j+1), pop  — collects at every node

# permutations: used-set or in-place swap
def dfs(path, used):
    if len(path) == len(nums):
        res.append(path.copy()); return
    for i, x in enumerate(nums):
        if used[i]: continue
        used[i] = True; path.append(x)
        dfs(path, used)
        path.pop(); used[i] = False

# combination sum (reuse allowed): pass start index i, recurse with i (not i+1)
# combination sum II / subsets II (dup input): sort, then skip dups at same level:
#   if j > i and nums[j] == nums[j - 1]: continue

# word search (grid): mark cell, recurse 4 dirs, restore cell
board[r][c] = '#'
found = any(dfs(nr, nc, k + 1) for nr, nc in nbrs)
board[r][c] = ch

# palindrome partitioning: for each prefix that's a palindrome, recurse on rest
# n-queens: cols, diag (r-c), anti-diag (r+c) sets; place row by row
```

## Dedup rule of thumb
Duplicates in INPUT → sort + skip equal siblings at the same tree level (`j > start and a[j] == a[j-1]`). Duplicates from REUSE → control via start index (i for reuse, i+1 for no reuse).

## Complexity
Subsets O(2^n · n), permutations O(n! · n), combination sums exponential — fine, n is small (≤ ~20). If n is bigger, it's a DP problem, not backtracking.

## Gotchas
- `res.append(path.copy())` / `path[:]` — appending `path` itself gives a list of empty lists.
- Un-choose must mirror choose exactly (pop what you appended, unmark what you marked).
- Prune early (sorted input + `if total > target: break`) — often the TLE fix.
