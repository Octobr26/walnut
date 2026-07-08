# Binary Search

## When
Sorted data, or any *monotonic* predicate ("smallest x where f(x) is true") — including search-on-answer (Koko bananas, ship capacity).

## Templates

```python
# exact target
l, r = 0, len(a) - 1
while l <= r:
    m = (l + r) // 2
    if a[m] == target: return m
    if a[m] < target: l = m + 1
    else: r = m - 1
return -1

# lower bound: first index where predicate true  (THE template to memorize)
l, r = 0, n                      # r = n, not n-1: answer may be "none"
while l < r:
    m = (l + r) // 2
    if ok(m):                    # monotone: F F F T T T
        r = m
    else:
        l = m + 1
return l                         # first True, or n if none

# search on answer space
lo, hi = 1, max(piles)
while lo < hi:
    m = (lo + hi) // 2
    if can_finish(m):            # feasibility is monotone in m
        hi = m
    else:
        lo = m + 1
return lo
```

## Rotated sorted array
One half is always sorted — check which, then check if target lies inside it:

```python
while l <= r:
    m = (l + r) // 2
    if a[m] == target: return m
    if a[l] <= a[m]:                       # left half sorted
        if a[l] <= target < a[m]: r = m - 1
        else: l = m + 1
    else:                                  # right half sorted
        if a[m] < target <= a[r]: l = m + 1
        else: r = m - 1
```

Find-min variant: compare `a[m]` with `a[r]`, move toward the unsorted side.

## Other classics
- 2-D matrix as flat array: `a[m // cols][m % cols]`.
- Median of two sorted arrays: partition the shorter array, binary search on cut position.
- Time-based KV store: bisect_right on timestamps minus 1.

## Gotchas
- `while l < r` + `r = m` never infinite-loops with `m = (l+r)//2` (rounds down). `l = m` without `+1` DOES loop — if you need it, use `m = (l+r+1)//2`.
- Prefer the lower-bound template for everything except exact-match; fewer edge cases.
- Answer-space bounds: lo must be feasible-exclusive-safe (often 1 or min), hi = something definitely feasible (max/sum).
