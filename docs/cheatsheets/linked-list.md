# Linked List

## Idioms

```python
# dummy head: kills "empty list / modify head" edge cases
dummy = ListNode(0, head)
prev = dummy
...
return dummy.next

# reverse (iterative — memorize cold)
prev, cur = None, head
while cur:
    cur.next, prev, cur = prev, cur, cur.next
return prev

# fast/slow: middle of list (slow ends at mid; for even length, second mid)
slow = fast = head
while fast and fast.next:
    slow = slow.next
    fast = fast.next.next

# cycle detection (Floyd)
slow = fast = head
while fast and fast.next:
    slow, fast = slow.next, fast.next.next
    if slow is fast: return True
return False
# cycle START: after meeting, reset one to head, advance both by 1 until equal

# kth from end: lead fast by k, advance together
```

## Composite patterns
- Reorder list = middle + reverse second half + merge alternate.
- Palindrome list = same, compare halves.
- Merge two sorted: dummy + tail, splice smaller; loop `while a and b`, then `tail.next = a or b`.
- Merge k lists: heap of `(val, i, node)` (i breaks ties — nodes aren't comparable), or pairwise merge.
- Remove n-th from end: dummy + fast/slow, gap n, stop when `fast.next` is None.
- Copy list with random pointer: dict `old -> new` in two passes, or interleave copies.
- LRU cache: dict + doubly-linked list with sentinel head/tail; helpers `_remove(node)`, `_add_front(node)`.

## Gotchas
- Draw it. Pointer updates in wrong order lose the rest of the list — save `nxt = cur.next` first (or use tuple assignment as above).
- `while fast and fast.next` — both checks, in that order.
- Compare nodes with `is`, not `==`.
- After splitting a list, terminate the first half: `mid_prev.next = None`.
