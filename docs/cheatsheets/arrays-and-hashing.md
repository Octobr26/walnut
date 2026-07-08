# Arrays & Hashing

## Core idea
Trade space for time: one pass building a hash map/set usually replaces a nested loop.

## Idioms

```python
# seen-set membership (duplicates, complements)
seen = set()
for x in nums:
    if x in seen: ...
    seen.add(x)

# value -> index (two-sum style: check complement BEFORE inserting)
idx = {}
for i, x in enumerate(nums):
    if target - x in idx:
        return [idx[target - x], i]
    idx[x] = i

# group by canonical key (anagrams: sorted string or char-count tuple)
groups = defaultdict(list)
for s in strs:
    groups[tuple(sorted(s))].append(s)      # or count-tuple key below

def key(s):                                  # O(len) key, no sort
    cnt = [0] * 26
    for ch in s:
        cnt[ord(ch) - ord('a')] += 1
    return tuple(cnt)

# frequency
cnt = Counter(nums)
cnt.most_common(k)                           # or bucket sort by count for O(n)

# prefix sums: sum(i..j) = pre[j+1] - pre[i]
pre = [0]
for x in nums:
    pre.append(pre[-1] + x)

# count subarrays with sum == k (prefix-sum + hashmap)
count = 0; cur = 0; freq = {0: 1}
for x in nums:
    cur += x
    count += freq.get(cur - k, 0)
    freq[cur] = freq.get(cur, 0) + 1
```

## Gotchas
- `in` on a list is O(n); on set/dict O(1).
- Dict/set keys must be hashable: use `tuple(lst)`, not `lst`.
- Sequence-in-place tricks: longest consecutive sequence -> set, only start counting when `x - 1 not in s`.
- Product-except-self: prefix pass then suffix pass, no division.

## Complexity targets
Most problems here: O(n) time, O(n) space. If you wrote a nested loop, look for the hash map.
