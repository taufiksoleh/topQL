# B-Tree Basics (Beginner Friendly)

## Why B-Trees
- Databases need fast lookups for queries like `WHERE age > 30` or `WHERE id = 42`.
- Scanning every row is slow (`O(n)`). A B-Tree gives `O(log n + k)` where `k` is matches returned.
- B-Trees stay balanced as data grows, so performance remains predictable.

## Mental Model
- Think of a sorted phonebook with bookmarks:
  - Pages contain multiple keys (not just one like a binary search tree).
  - Pointers guide you to child pages with ranges of keys.
  - The tree is kept balanced: all leaves are at the same level.

```
          [ 20 | 50 ]
         /           \
   [ 5 | 12 ]     [ 34 | 45 | 70 ]
```
- Searching follows ranges: to find `34`, you choose the right child (since 34 > 20) then the left slot on that page.

## Core Operations
- Search: navigate by comparing the target to keys on each node; stop at a leaf; return matches.
- Insert: place key in sorted order; if a node overflows, split and promote a middle key up.
- Delete: remove key; if a node underflows, borrow or merge with neighbors to keep balance.

## Big-O (Typical)
- Search: `O(log n)`
- Insert/Delete: `O(log n)`
- Range query (e.g., `>= x`): `O(log n + k)` by locating `x` then scanning forward.

## B-Tree vs B+Tree
- B-Tree: stores keys and values in both internal nodes and leaves.
- B+Tree: stores all values only in leaves; internal nodes are routing. Leaves form a linked list for fast range scans.
- Many databases use B+Trees for faster range iteration. The mental model here applies to both.

## How TopQL Uses It
- We added a simple index per column to accelerate `WHERE` filtering. It mimics B-Tree behavior using a sorted array plus binary search.
- Index code: `btree_index.py:4` (`class BTreeIndex`)
- Table integration points:
  - Import: `topql.py:16`
  - Table fields and index setup: `topql.py:515`
  - Insert updates indexes: `topql.py:528`
  - WHERE uses indexes: `topql.py:642`
  - Update maintains indexes: `topql.py:570`
  - Delete maintains indexes: `topql.py:582`

### Simplified Index Internals
- Keys are kept sorted; each key maps to a set of row IDs.
- We use Python’s `bisect` to do fast binary search:
  - `=`: locate exact key; return its row IDs.
  - `!=`: combine all row IDs except the target.
  - `<, <=`: take keys before the boundary.
  - `>, >=`: take keys after the boundary.
- This gives the same asymptotic benefits as a B-Tree for queries without building full tree nodes.

## Example
- Suppose a table `users(id, name, age, active)` with many rows.
- Query: `SELECT * FROM users WHERE age >= 30 AND active = TRUE`
  - Index lookup for `age >= 30` returns row ID set A.
  - Index lookup for `active = TRUE` returns row ID set B.
  - Combine with `AND`: `A ∩ B` to get final matches.

## Benefits
- Large speedups for equality and range predicates in `WHERE`.
- Predictable performance as data grows (logarithmic search cost).

## Caveats
- Extra memory to store indexes.
- Inserts/updates/deletes must maintain indexes.
- `ORDER BY` still sorts in memory; indexing can be extended to help ordering.

## Where To Explore Next
- Read `btree_index.py:4` to see query methods.
- See how `Table._filter_rows` combines index results: `topql.py:642`.
- Try running example queries in `examples.py` to observe behavior.

