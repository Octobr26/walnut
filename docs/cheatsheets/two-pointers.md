# Two Pointers

## When
Sorted array (or sortable), palindromes, pair-with-condition, in-place partition. Converging ends or fast/slow.

## Templates

```python
# converging (two-sum on sorted, valid palindrome, container water)
l, r = 0, len(a) - 1
while l < r:
    if condition_met(a[l], a[r]):
        ...
    elif need_bigger:
        l += 1
    else:
        r -= 1

# 3sum: sort, fix i, two-pointer the rest; skip duplicates
nums.sort()
for i in range(len(nums) - 2):
    if i and nums[i] == nums[i - 1]:
        continue
    l, r = i + 1, len(nums) - 1
    while l < r:
        s = nums[i] + nums[l] + nums[r]
        if s < 0: l += 1
        elif s > 0: r -= 1
        else:
            res.append([nums[i], nums[l], nums[r]])
            l += 1
            while l < r and nums[l] == nums[l - 1]:
                l += 1

# slow/fast writer (remove duplicates / move zeros, in place)
w = 0
for r in range(len(a)):
    if keep(a[r]):
        a[w] = a[r]
        w += 1
```

## Why converging works
Moving the pointer at the *limiting* side never discards the optimum — argue this to yourself per problem (container-with-water: shorter wall can never do better, move it).

## Gotchas
- Skip-duplicate lines go AFTER taking a valid answer, and compare against previous index.
- Trapping rain water: track `max_left` / `max_right`, move the smaller side.
- `while l < r` vs `l <= r`: pairs need `<`, single-element checks may need `<=`.

## Complexity
O(n) after optional O(n log n) sort, O(1) extra space — that's the point of the pattern.
