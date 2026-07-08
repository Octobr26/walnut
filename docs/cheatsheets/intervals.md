# Intervals

## The one rule
Sort first. By START for merging/inserting, by END for max-non-overlapping (activity selection).

## Templates

```python
# overlap test (touching counts per problem statement!)
a_start < b_end and b_start < a_end        # strict: touching does NOT overlap
a_start <= b_end and b_start <= a_end      # touching DOES overlap

# merge intervals
intervals.sort(key=lambda i: i[0])
merged = [intervals[0]]
for s, e in intervals[1:]:
    if s <= merged[-1][1]:                 # overlaps (or touches) last
        merged[-1][1] = max(merged[-1][1], e)
    else:
        merged.append([s, e])

# insert interval: emit before-parts, merge all overlapping into one, emit rest
res = []
i = 0
while i < n and intervals[i][1] < new[0]: res.append(intervals[i]); i += 1
while i < n and intervals[i][0] <= new[1]:
    new = [min(new[0], intervals[i][0]), max(new[1], intervals[i][1])]; i += 1
res.append(new)
res += intervals[i:]

# min removals for non-overlap (erase overlap intervals): sort by END, greedy keep
intervals.sort(key=lambda i: i[1])
end = -inf; keep = 0
for s, e in intervals:
    if s >= end:
        keep += 1; end = e
return len(intervals) - keep

# meeting rooms II (min rooms): sweep line
starts = sorted(s for s, _ in intervals)
ends = sorted(e for _, e in intervals)
rooms = best = j = 0
for s in starts:
    while ends[j] <= s: ...                # or two-pointer count version
# alt: heap of end times — push end, pop while h[0] <= start, rooms = max(rooms, len(h))

# event count version: +1 at start, -1 at end, sort events, running max
```

## Which sort key
| Goal | Sort by |
|---|---|
| merge / insert | start |
| keep max non-overlapping / min removals | end |
| min rooms / max concurrent | sweep both boundaries |

## Gotchas
- Read whether `[1,2]` and `[2,3]` overlap in THIS problem — flips `<=` vs `<` everywhere.
- Meeting rooms II with events: process end before start at equal time if touching is allowed.
- Mutate `merged[-1][1]` with max — later interval can be fully inside an earlier one.
