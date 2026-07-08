# Greedy

## Mindset
Pick the locally best move that provably never blocks the global optimum. If you can't sketch the exchange argument ("any optimal solution can be rewritten to start with my greedy choice"), suspect it's DP instead.

## Classics

```python
# max subarray (Kadane — greedy view: drop negative prefixes)
cur = best = nums[0]
for x in nums[1:]:
    cur = max(x, cur + x)
    best = max(best, cur)

# jump game: track farthest reachable
far = 0
for i, x in enumerate(nums):
    if i > far: return False
    far = max(far, i + x)
return True

# jump game II (min jumps): BFS-like layers
jumps = end = far = 0
for i in range(len(nums) - 1):
    far = max(far, i + nums[i])
    if i == end:                 # exhausted current layer
        jumps += 1
        end = far

# gas station: if total gas >= total cost an answer exists;
# restart candidate after any failure point
tank = start = 0
for i in range(n):
    tank += gas[i] - cost[i]
    if tank < 0:
        start, tank = i + 1, 0

# partition labels: last index of each char; extend window to furthest last-seen
last = {ch: i for i, ch in enumerate(s)}
l = r = 0
for i, ch in enumerate(s):
    r = max(r, last[ch])
    if i == r:
        res.append(r - l + 1); l = i + 1

# hand of straights: Counter + always extend from current minimum (heap or sorted keys)

# merge triplets: only triplets with no coordinate exceeding target can be used;
# check the usable ones cover each target coordinate
```

## Common greedy signals
- "Can you reach / is it possible" → track a running bound (farthest, tank, max).
- Sort by the RIGHT key first: intervals by end (max non-overlap), pairs by ratio/diff.
- Counterexample check: if a small case breaks your greedy, it's DP.

## Gotchas
- Jump II: loop stops at `len - 1`; incrementing at `i == end` counts layers, not steps.
- Gas station correctness leans on the "total >= 0 ⇒ unique valid start" lemma — don't re-scan O(n^2).
- Greedy + sort is O(n log n); if your greedy needs lookahead, that's the DP smell.
