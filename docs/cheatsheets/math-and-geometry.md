# Math & Geometry

## Matrix manipulation

```python
# rotate 90° clockwise IN PLACE: transpose, then reverse each row
for r in range(n):
    for c in range(r + 1, n):              # c > r: swap once
        m[r][c], m[c][r] = m[c][r], m[r][c]
for row in m:
    row.reverse()
# counterclockwise: transpose + reverse each COLUMN (or reverse rows first)

# spiral order: four boundaries, shrink after each side
top, bot, left, right = 0, R - 1, 0, C - 1
while top <= bot and left <= right:
    for c in range(left, right + 1): out(m[top][c])
    top += 1
    for r in range(top, bot + 1): out(m[r][right])
    right -= 1
    if top <= bot:                          # guard: single row remaining
        for c in range(right, left - 1, -1): out(m[bot][c])
        bot -= 1
    if left <= right:                       # guard: single column remaining
        for r in range(bot, top - 1, -1): out(m[r][left])
        left += 1

# set matrix zeroes O(1) space: first row/col as marker storage,
# separate flag for first row itself; zero from bottom-right of markers
```

## Number tricks

```python
# happy number: cycle detection — seen-set or Floyd on digit-square-sum
# digits: while n: n, d = divmod(n, 10)

# plus one: carry from the right; all-9s -> [1] + [0]*n

# pow(x, n) fast exponentiation, O(log n)
def mypow(x, n):
    if n < 0: x, n = 1 / x, -n
    res = 1
    while n:
        if n & 1: res *= x
        x *= x
        n >>= 1
    return res

# multiply strings: res[i + j + 1] accumulates digit products, carry pass after
res = [0] * (len(a) + len(b))
for i in reversed(range(len(a))):
    for j in reversed(range(len(b))):
        res[i + j + 1] += int(a[i]) * int(b[j])
# then: for k in reversed(range(1, len(res))): res[k-1] += res[k] // 10; res[k] %= 10
```

## Python-specific number facts
- Ints are arbitrary precision — no overflow, but problems may still ask you to SIMULATE 32-bit.
- `-7 // 2 == -4` (floors); C-style truncation = `int(-7 / 2) == -3`.
- `%` follows floor too: `-7 % 3 == 2`. For C-style remainder use `math.fmod`.
- `round()` is banker's rounding: `round(2.5) == 2`.

## Gotchas
- Rotate: transpose swaps with `c > r` only, else you swap back.
- Spiral: the two `if` guards prevent double-walking a single leftover row/column.
- Geometry rarely needs trig here — it's index manipulation.
