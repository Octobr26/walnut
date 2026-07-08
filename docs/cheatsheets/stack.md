# Stack

## When
Matching/nesting (parentheses), most-recent-unresolved-item problems, "next greater/smaller element", expression evaluation. Python stack = plain list: `append` / `pop` / `stack[-1]`.

## Templates

```python
# matching pairs
pairs = {')': '(', ']': '[', '}': '{'}
st = []
for ch in s:
    if ch in pairs:
        if not st or st.pop() != pairs[ch]:
            return False
    else:
        st.append(ch)
return not st

# monotonic decreasing stack -> next greater element
st = []                          # indices, values strictly decreasing
for i, x in enumerate(nums):
    while st and nums[st[-1]] < x:
        j = st.pop()
        res[j] = x               # x is next greater for j
    st.append(i)

# daily temperatures: same shape, res[j] = i - j

# largest rectangle in histogram
st = []                          # indices, heights increasing
for i, h in enumerate(heights + [0]):        # sentinel flushes stack
    start = i
    while st and st[-1][1] > h:
        idx, height = st.pop()
        best = max(best, height * (i - idx))
        start = idx
    st.append((start, h))
```

## Monotonic stack: how to pick direction
- "next greater" → keep stack decreasing, pop while `top < current`.
- "next smaller" → keep stack increasing, pop while `top > current`.
- Store indices when you need distances or positions.

## Other classics
- Min stack: push pairs `(x, min(x, st[-1][1]))` — O(1) getMin.
- Reverse Polish: push numbers, pop two on operator (`b op a` order! pop gives `a` then `b` → compute `b op a`).
- Generate parentheses: backtracking with `open < n`, `close < open`.
- Car fleet: sort by position desc, stack of arrival times; fleet merges when `time <= st[-1]`.

## Gotchas
- Truncating division toward zero for RPN: `int(b / a)`, not `b // a` (negative operands).
- Empty-stack checks before `pop`/`[-1]` — most bugs here.
- Each index pushed/popped once → O(n) despite nested while.
