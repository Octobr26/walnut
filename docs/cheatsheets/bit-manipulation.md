# Bit Manipulation

## Operator toolkit

```python
x & 1            # last bit / parity
x >> 1, x << 1   # halve / double
x & (x - 1)      # clear lowest set bit  (Kernighan)
x & (-x)         # isolate lowest set bit
x ^ y            # add without carry; a ^ a == 0; a ^ 0 == a
1 << k           # bit k mask
x | (1 << k)     # set bit k
x & ~(1 << k)    # clear bit k
(x >> k) & 1     # test bit k
bin(x).count('1')  # or x.bit_count() (3.8: use bin().count)
```

## Classics

```python
# single number (all others twice): XOR everything
res = 0
for x in nums: res ^= x

# count bits 0..n (DP on bits)
dp = [0] * (n + 1)
for i in range(1, n + 1):
    dp[i] = dp[i >> 1] + (i & 1)          # or dp[i & (i-1)] + 1

# hamming weight: count with x &= x - 1 loop (runs once per set bit)

# reverse 32 bits
res = 0
for _ in range(32):
    res = (res << 1) | (n & 1)
    n >>= 1

# missing number: XOR indices 0..n with values (or sum formula n*(n+1)//2 - sum)

# sum of two integers WITHOUT +/- : loop carry
MASK, MAX = 0xFFFFFFFF, 0x7FFFFFFF
def add(a, b):
    while b:
        a, b = (a ^ b) & MASK, ((a & b) << 1) & MASK
    return a if a <= MAX else ~(a ^ MASK)  # fold back to signed
```

## Python 32-bit simulation (the real trap)
Python ints never overflow and negatives have infinite leading 1s conceptually:
- Mask after every op: `x & 0xFFFFFFFF`.
- Reinterpret as signed at the end: `x if x <= 0x7FFFFFFF else ~(x ^ 0xFFFFFFFF)` (equivalently `x - (1 << 32)`).
- Right-shifting negatives never terminates a `while n:` loop — mask first or bound the loop to 32 iterations.

## Bitmask as a set (crosses into DP/backtracking)
```python
mask | (1 << i)      # add element i
mask & (1 << i)      # contains i?
mask ^ (1 << i)      # toggle
for sub in all 2^n: for mask in range(1 << n): ...
```

## Gotchas
- XOR tricks need "everything pairs up except one" — verify the invariant.
- `x & (x-1) == 0` tests power of two (with `x > 0` check).
- Operator precedence: `&`/`|`/`^` bind LOOSER than `==` — parenthesize: `(x & 1) == 0`.
