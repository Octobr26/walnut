# Tries

## Node + insert/search (memorize)

```python
class TrieNode:
    def __init__(self):
        self.children = {}          # char -> TrieNode  (dict beats [None]*26 for clarity)
        self.end = False            # word terminates here

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        cur = self.root
        for ch in word:
            cur = cur.children.setdefault(ch, TrieNode())
        cur.end = True

    def search(self, word):
        cur = self.root
        for ch in word:
            cur = cur.children.get(ch)
            if not cur: return False
        return cur.end              # startsWith: return True here instead
```

## Wildcard search ('.' matches any) — DFS branch on dot

```python
def search(self, word):
    def dfs(i, node):
        for j in range(i, len(word)):
            ch = word[j]
            if ch == '.':
                return any(dfs(j + 1, child) for child in node.children.values())
            node = node.children.get(ch)
            if not node: return False
        return node.end
    return dfs(0, self.root)
```

## Word Search II (board + word list) — the trie payoff
Build trie of words, DFS the board walking board and trie together:

```python
def dfs(r, c, node, path):
    ch = board[r][c]
    nxt = node.children.get(ch)
    if not nxt: return
    if nxt.end:
        res.append(path + ch)
        nxt.end = False                  # dedupe
    board[r][c] = '#'                    # visited marker
    for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
        if 0 <= r+dr < R and 0 <= c+dc < C:
            dfs(r+dr, c+dc, nxt, path + ch)
    board[r][c] = ch
```

Optimizations if TLE: store word at end-node instead of rebuilding path; prune empty child branches after finding words.

## When a trie
Prefix queries, many-strings shared-prefix compression, wildcard matching, word games on grids. Cost: O(L) per op, memory O(total chars).

## Gotchas
- Mark `end` on the LAST node, check `end` (not just node existence) for full-word search.
- `setdefault` is the clean insert one-liner; don't `if ch not in ...` dance.
- Restore board cell after DFS (backtrack) — classic miss.
