# Heap / Priority Queue

## heapq essentials (min-heap ONLY)

```python
import heapq
heapq.heapify(h)                 # O(n) in place
heapq.heappush(h, x)             # O(log n)
x = heapq.heappop(h)             # O(log n), pops MIN
h[0]                             # peek, O(1)

# max-heap: negate on the way in and out
heapq.heappush(h, -x);  x = -heapq.heappop(h)

# tuples: compares first element, then second (tie-break)
heapq.heappush(h, (priority, item))
# if items aren't comparable, add a counter: (priority, i, item)
```

## Patterns

```python
# top-k / kth largest: MIN-heap of size k (smallest of the k is root)
h = []
for x in nums:
    heapq.heappush(h, x)
    if len(h) > k:
        heapq.heappop(h)
# h[0] is the kth largest; O(n log k)

# k closest points: heap of (dist, x, y), same size-k trick
# or heapq.nsmallest(k, points, key=lambda p: p[0]**2 + p[1]**2)

# streaming median: two heaps
small = []   # max-heap (negated) — lower half
large = []   # min-heap — upper half
def add(x):
    heapq.heappush(small, -x)
    heapq.heappush(large, -heapq.heappop(small))   # rebalance order
    if len(large) > len(small):
        heapq.heappush(small, -heapq.heappop(large))
def median():
    return -small[0] if len(small) > len(large) else (-small[0] + large[0]) / 2

# task scheduler / frequency: max-heap of counts + cooldown queue of (ready_time, count)

# lazy deletion: heap holds stale entries; on pop, skip if not current
while h and is_stale(h[0]):
    heapq.heappop(h)
```

## heappushpop vs heapreplace
- `heappushpop(h, x)`: push x, then pop min — returns x itself if x ≤ everything.
- `heapreplace(h, x)`: pop min FIRST, then push x — pops even if x would be the new min.

## When heap vs sort
- Need only k best of n, or data streams in → heap, O(n log k).
- Have everything up front and need full order → sort.
- Kth largest one-shot alternative: quickselect, average O(n).

## Gotchas
- No decrease-key in heapq — use lazy deletion (push duplicate, skip stale on pop).
- `heapq.nlargest/nsmallest` take `key=`; great for one-liners, still O(n log k).
- Custom objects: push tuples, or define `__lt__`.
