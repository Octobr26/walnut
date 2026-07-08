# Advanced Graphs

## Dijkstra — shortest path, weighted, non-negative

```python
import heapq
dist = {src: 0}
h = [(0, src)]
while h:
    d, u = heapq.heappop(h)
    if d > dist.get(u, math.inf):        # stale entry, skip (lazy deletion)
        continue
    for v, w in adj[u]:
        nd = d + w
        if nd < dist.get(v, math.inf):
            dist[v] = nd
            heapq.heappush(h, (nd, v))
# O(E log V). Variant "network delay": answer = max(dist.values()) or -1.
```

## Prim's — minimum spanning tree (min cost to connect all points)

```python
seen = set()
h = [(0, 0)]                             # (cost, node)
total = 0
while len(seen) < n:
    cost, u = heapq.heappop(h)
    if u in seen: continue
    seen.add(u); total += cost
    for v, w in nbrs(u):
        if v not in seen:
            heapq.heappush(h, (w, v))
```
Kruskal alternative: sort edges, union-find, take edges that union.

## Bellman-Ford / limited steps (cheapest flights ≤ k stops)

```python
dist = [inf] * n; dist[src] = 0
for _ in range(k + 1):                   # at most k+1 edges
    nxt = dist[:]                        # RELAX FROM SNAPSHOT — the key detail
    for u, v, w in edges:
        if dist[u] + w < nxt[v]:
            nxt[v] = dist[u] + w
    dist = nxt
```

## Modified-Dijkstra family
State can be more than a node: `(effort, r, c)` for path-max-min problems (swim in water, path with min effort) — "distance" = max edge/cell so far. If it fits "minimize the worst step", it's this.

## Eulerian path (reconstruct itinerary) — Hierholzer

```python
adj = defaultdict(list)                  # sort/reverse tickets for lexical order
for a, b in sorted(tickets, reverse=True):
    adj[a].append(b)
route = []
def dfs(u):
    while adj[u]:
        dfs(adj[u].pop())                # pop = O(1), consumes edge
    route.append(u)                      # POSTorder
dfs("JFK")
return route[::-1]
```

## Choosing the algorithm
| Situation | Use |
|---|---|
| unweighted shortest path | BFS |
| weighted, non-negative | Dijkstra |
| weighted, ≤ k edges / negative | Bellman-Ford (snapshot) |
| connect-all-min-cost | Prim / Kruskal |
| minimize max step on path | modified Dijkstra / binary search + BFS |
| use every edge once | Hierholzer |

## Gotchas
- Dijkstra: skip stale pops (`if d > dist[u]: continue`) — heapq has no decrease-key.
- Bellman-Ford without the snapshot copy lets one round use multiple new edges → wrong for k-stops.
- Hierholzer appends postorder; reverse at the end.
