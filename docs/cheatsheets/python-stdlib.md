# Python stdlib for interviews

## collections

```python
from collections import defaultdict, Counter, deque

d = defaultdict(list)       # missing key -> []; also defaultdict(int), defaultdict(set)
d["k"].append(1)            # no KeyError, no setdefault dance

c = Counter("aabbbc")       # {'b': 3, 'a': 2, 'c': 1}
c.most_common(2)            # [('b', 3), ('a', 2)]
c["missing"]                # 0, never KeyError
Counter(a) == Counter(b)    # anagram check
c1 - c2                     # subtract, drops zero/negative counts

q = deque([1, 2, 3])
q.append(4); q.appendleft(0)    # O(1) both ends
q.pop(); q.popleft()            # O(1) both ends  (list.pop(0) is O(n)!)
q = deque(maxlen=3)             # auto-evicts oldest
```

## heapq (min-heap only)

```python
import heapq

h = [3, 1, 4]
heapq.heapify(h)                 # O(n), in place
heapq.heappush(h, 2)             # O(log n)
smallest = heapq.heappop(h)      # O(log n)
h[0]                             # peek min, O(1)

# max-heap: negate values
heapq.heappush(h, -val); biggest = -heapq.heappop(h)

# tuples compare element-wise -> priority queue
heapq.heappush(h, (dist, node))

# k largest / smallest
heapq.nlargest(k, nums)          # also takes key=
heapq.nsmallest(k, nums, key=lambda x: x[1])

heapq.heappushpop(h, x)          # push then pop  (faster than push + pop)
heapq.heapreplace(h, x)          # pop then push  (pops even if x is smaller!)
```

## bisect (sorted lists)

```python
import bisect

a = [1, 3, 3, 5]
bisect.bisect_left(a, 3)    # 1 -> first index where 3 could go (leftmost)
bisect.bisect_right(a, 3)   # 3 -> past the last 3
bisect.insort(a, 4)         # insert keeping sorted, O(n) due to shift

# count of x in sorted list:
bisect.bisect_right(a, x) - bisect.bisect_left(a, x)
```

## sorting

```python
nums.sort()                          # in place, stable, O(n log n)
sorted(nums, reverse=True)           # new list
sorted(pairs, key=lambda p: (p[0], -p[1]))   # asc first, desc second
sorted(words, key=len)
intervals.sort(key=lambda i: i[0])   # classic intervals prep

# custom comparator (rare, e.g. largest-number problems)
from functools import cmp_to_key
sorted(strs, key=cmp_to_key(lambda a, b: -1 if a + b > b + a else 1))
```

## strings & chars

```python
ord('a')                    # 97;  chr(97) -> 'a'
ord(ch) - ord('a')          # 0..25 bucket index
s.isdigit(), s.isalpha(), s.isalnum(), s.lower()
"".join(parts)              # build strings with list + join, never += in a loop
s.split()                   # splits on any whitespace, drops empties
s[::-1]                     # reversed copy
```

## slicing & iteration gotchas

```python
a[i:j]                # copy, O(j-i); excludes j
a[::-1]               # reversed copy
a[:]                  # shallow copy
[[0] * cols for _ in range(rows)]     # 2-D init
# NOT [[0]*cols]*rows  -> rows alias the SAME list

for i, x in enumerate(nums): ...
for a, b in zip(xs, ys): ...
for x in reversed(nums): ...          # no copy, unlike nums[::-1]
range(n - 1, -1, -1)                  # indices n-1 .. 0
```

## misc that saves minutes

```python
float("inf"), float("-inf")
divmod(17, 5)               # (3, 2)
math.inf, math.gcd(a, b), math.isqrt(n)
x // y                      # floor div: -7 // 2 == -4 (floors toward -inf!)
int(-7 / 2)                 # -3 (truncates) — careful porting C algorithms
set/frozenset               # frozenset hashable -> usable as dict key
tuple(lst)                  # hashable list for memo keys
functools.lru_cache(None)   # memoize recursion: @lru_cache(maxsize=None)
itertools: permutations, combinations, product, accumulate
```
