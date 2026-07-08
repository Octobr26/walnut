# Complexity reference

## Data structure operations

| Structure | Access | Search | Insert | Delete | Notes |
|---|---|---|---|---|---|
| list | O(1) | O(n) | append O(1)* | pop() O(1), pop(0) O(n) | insert(0, x) O(n) |
| dict | — | O(1)* | O(1)* | O(1)* | worst O(n), never in practice |
| set | — | O(1)* | O(1)* | O(1)* | `in` on list is O(n)! |
| deque | O(n) mid | O(n) | O(1) both ends | O(1) both ends | indexing middle is slow |
| heapq | O(1) min | O(n) | O(log n) | pop-min O(log n) | heapify O(n) |
| sorted list + bisect | O(1) | O(log n) | O(n) shift | O(n) | fine when inserts are rare |

## Algorithm costs

| Pattern | Time | Space |
|---|---|---|
| sort | O(n log n) | O(n) (timsort) |
| binary search | O(log n) | O(1) |
| two pointers / sliding window | O(n) | O(1) |
| hash map pass | O(n) | O(n) |
| heap of k over n items | O(n log k) | O(k) |
| DFS/BFS | O(V + E) | O(V) |
| Dijkstra (heap) | O(E log V) | O(V) |
| topological sort | O(V + E) | O(V) |
| union-find (path compr + rank) | ~O(α(n)) ≈ O(1) per op | O(n) |
| trie insert/search word len L | O(L) | O(total chars) |
| backtracking subsets | O(2^n) | O(n) depth |
| backtracking permutations | O(n · n!) | O(n) depth |
| 1-D DP | O(n) or O(n·k) | often O(1) after rolling |
| 2-D DP | O(m·n) | O(min(m, n)) with rolling row |

## Input size → intended complexity (rule of thumb)

| n up to | Likely intended |
|---|---|
| 10–12 | O(n!) / O(2^n · n) backtracking |
| 20–25 | O(2^n) bitmask/subsets |
| ~100 | O(n^3) |
| ~1 000 | O(n^2) |
| ~100 000 | O(n log n) |
| ~1 000 000+ | O(n) or O(n log n) tight |

## String / recursion gotchas

- `s += ch` in a loop is O(n^2); build a list, `"".join` at the end.
- Slicing (`a[i:]`) copies — recursion passing slices turns O(n) into O(n^2); pass indices.
- Python recursion limit ~1000: `sys.setrecursionlimit(...)` or convert to iterative for deep trees/graphs.
