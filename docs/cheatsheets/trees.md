# Trees

## Traversal templates

```python
# DFS recursive (preorder shown; move the visit line for in/post)
def dfs(node):
    if not node: return
    visit(node)          # pre
    dfs(node.left)
    # visit(node) here = inorder (sorted order for BST!)
    dfs(node.right)
    # visit(node) here = postorder (children before parent — use for heights)

# BFS level order
q = deque([root])
while q:
    level = []
    for _ in range(len(q)):          # freeze level size
        node = q.popleft()
        level.append(node.val)
        if node.left: q.append(node.left)
        if node.right: q.append(node.right)
    res.append(level)

# iterative inorder (stack)
st, cur = [], root
while st or cur:
    while cur:
        st.append(cur); cur = cur.left
    cur = st.pop()
    visit(cur)
    cur = cur.right
```

## Recursion shapes
Most tree problems are one of:

```python
# 1. return a value up (height, sum, balanced)
def height(node):
    if not node: return 0
    return 1 + max(height(node.left), height(node.right))

# 2. global best updated in postorder (diameter, max path sum)
def gain(node):
    if not node: return 0
    l, r = max(gain(node.left), 0), max(gain(node.right), 0)
    self.best = max(self.best, node.val + l + r)   # path through node
    return node.val + max(l, r)                    # path continuing up

# 3. pass constraints down (validate BST)
def valid(node, lo, hi):
    if not node: return True
    if not (lo < node.val < hi): return False
    return valid(node.left, lo, node.val) and valid(node.right, node.val, hi)
```

## BST specifics
- Inorder = sorted. Kth smallest = inorder, count down.
- LCA in BST: walk from root; split point (one value each side) is the answer.
- LCA general tree: postorder — return node if it is p/q or both sides returned non-null.

## Serialization
Preorder with null markers ("N") + iterator/index rebuild; or BFS with nulls.

## Gotchas
- `if not node` base case FIRST, always.
- Height vs depth vs diameter: diameter counts edges through any node, not through root only.
- Same-tree/subtree: compare structure AND values; subtree = same(s, t) at every node of s.
- Python recursion limit on deep skewed trees → iterative or `sys.setrecursionlimit(10**6)`.
