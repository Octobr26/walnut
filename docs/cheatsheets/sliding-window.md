# Sliding Window

## When
Contiguous subarray/substring, "longest/shortest/count ... satisfying constraint". Window validity must be monotone: growing can only break it, shrinking can only fix it.

## Templates

```python
# variable window, LONGEST valid
l = 0
best = 0
state = {}                       # counts, distinct, etc.
for r, x in enumerate(s):
    add(state, x)                # extend right
    while invalid(state):        # shrink until valid again
        remove(state, s[l])
        l += 1
    best = max(best, r - l + 1)

# variable window, SHORTEST valid (min window substring shape)
l = 0
best = math.inf
for r, x in enumerate(s):
    add(state, x)
    while valid(state):          # note: shrink while VALID here
        best = min(best, r - l + 1)
        remove(state, s[l])
        l += 1

# fixed window size k
for r in range(len(a)):
    add(a[r])
    if r >= k:
        remove(a[r - k])
    if r >= k - 1:
        best = max(best, window_value)
```

## State choices
- distinct chars: `Counter` + `len(counter)`; delete keys at zero or track nonzero count.
- anagram/permutation-in-string: two count arrays, track `matches == 26`.
- min-window-substring: `need` Counter + `have` counter of satisfied chars.
- longest repeating char replacement: `window_len - max_freq_in_window > k` → shrink. `max_freq` may go stale; it's still correct for the MAX answer (classic subtlety).

## Monotonic deque (sliding window maximum)

```python
dq = deque()                     # indices, values decreasing
for r, x in enumerate(nums):
    while dq and nums[dq[-1]] <= x:
        dq.pop()
    dq.append(r)
    if dq[0] <= r - k:
        dq.popleft()
    if r >= k - 1:
        res.append(nums[dq[0]])
```

## Gotchas
- Every element enters and leaves the window once → O(n), even with the inner while.
- Window length is `r - l + 1`. Off-by-one lives here.
- If validity isn't monotone (e.g. "exactly k"), use `atMost(k) - atMost(k-1)`.
