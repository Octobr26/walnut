# Graphs

## Build + traverse

```python
# adjacency list from edges
adj = defaultdict(list)
for u, v in edges:
    adj[u].append(v)
    adj[v].append(u)          # undirected

# DFS (recursive)
seen = set()
def dfs(u):
    seen.add(u)
    for v in adj[u]:
        if v not in seen:
            dfs(v)

# BFS (shortest path in UNWEIGHTED graph)
q = deque([src]); seen = {src}; dist = 0
while q:
    for _ in range(len(q)):
        u = q.popleft()
        for v in adj[u]:
            if v not in seen:
                seen.add(v)          # mark on ENQUEUE, not dequeue
                q.append(v)
    dist += 1

# grid as graph
for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
    nr, nc = r + dr, c + dc
    if 0 <= nr < R and 0 <= nc < C and grid[nr][nc] == target: ...
```

## Topological sort (Kahn's / BFS)

```python
indeg = [0] * n
for u, v in edges:          # u -> v
    adj[u].append(v); indeg[v] += 1
q = deque(u for u in range(n) if indeg[u] == 0)
order = []
while q:
    u = q.popleft(); order.append(u)
    for v in adj[u]:
        indeg[v] -= 1
        if indeg[v] == 0: q.append(v)
# len(order) < n  ->  cycle (course schedule)
```

## Union-Find

```python
parent = list(range(n)); rank = [0] * n
def find(x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]      # path halving
        x = parent[x]
    return x
def union(a, b):
    ra, rb = find(a), find(b)
    if ra == rb: return False              # already connected (cycle!)
    if rank[ra] < rank[rb]: ra, rb = rb, ra
    parent[rb] = ra
    rank[ra] += rank[ra] == rank[rb]
    return True
```

## Pattern → problem map
- Count islands / connected components: DFS/BFS flood fill, or union-find.
- Multi-source spread (rotting oranges): BFS seeded with ALL sources.
- Border-inward (pacific-atlantic, surrounded regions): DFS from edges, invert.
- Clone graph: BFS/DFS with `old -> new` map, create on first sight.
- Valid tree: n-1 edges + fully connected (or union-find finds no cycle).
- Cycle in DIRECTED graph: 3-color DFS (white/gray/black; gray hit = cycle) or Kahn's.

## Gotchas
- BFS: mark visited when enqueuing — else duplicates blow up the queue.
- Grid DFS mutating input as visited-marker is fine; restore only if problem needs it.
- Recursion depth on big grids → iterative stack or setrecursionlimit.
