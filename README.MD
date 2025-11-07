# Gaming Leaderboard — README
## *By Richard Phan*

### Description
#### This is a command line Gaming Leaderboard that ingests player scores over time, keeping a history per player
#### and can produce ranked leaderboards on demand using a heapsort created from scratch.
---

### Linked List/Vector/heap-sort Design & Invariants

**Players & Registry**
- `Player { name: str, best: int|None, head: ScoreNode|None, next: Player|None }`
- **Registry** is a **singly linked list** of players (head-insertion).  
  - *Invariant:* `count` equals number of nodes reachable from `head` with no cycles.

**Score History (per player)**
- Singly **linked list** (`ScoreNode { value: int, next }`), **most-recent at head**.  
  - *Invariants:*  
    - Head is latest score.  
    - Traversal yields scores in reverse chronological order.  
    - `best` is `None` iff history empty; otherwise `best >= any score` in list.

**Vector (Dynamic Array)**
- Manual-resize array with `_data`, `_size`, `_capacity`.  
- Ops: `push_back`, `get`, `set`, `swap`, `length` (and a small internal `_grow()` doubling capacity).  
  - *Invariants:*  
    - `0 ≤ _size ≤ _capacity`  
    - Elements stored only in `[0 .. _size-1]`.

**Heap Sort (Max-Heap)**
- Build **max-heap** over a **snapshot Vector** of players (not the live registry).  
- Comparison: **(best desc, name asc)**; `None` treated as `-∞`.  
- Standard heapsort leaves array **worst→best** at indices `0..n-1`; we **print from the end** to get **best→worst**.  
  - *Invariants:*  
    - Heap property holds during build/extract.  
    - Snapshot does not mutate player nodes or histories.



---

### Run Instructions

**Run in the terminal of your IDE of choice (Pycharm, VS Code, etc)**
```
python3 main.py commands.txt
```
- Ensure the `commands.txt` file is in the same project directory as `main.py`
- Error message: `USAGE: <program> <commands_file>` results from 
- missing or invalid paths.
- Program is **non-interactive**; it reads the file, processes line-by-line, and exits.

---



## Commands

- `ADD_PLAYER name`  
  - Adds a new player with empty history (`best=None`). Duplicate → `DUPLICATE`.  
  - Edge cases: empty name → `ERROR: Player name cannot be empty`.

- `ADD_SCORE name score`  
  - Push score at history head; update `best` if higher. Missing player → `NOT FOUND`.  
  - Edge cases: non-integer → `ERROR: Invalid score value - must be an integer`;  
    out of 32-bit range → `ERROR: Score out of valid range`.

- `CURRENT name`  
  - Most recent score; missing player → `NOT FOUND`.

- `BEST name`  
  - Prints `best`; missing player → `NOT FOUND`.

- `HISTORY name k`  
  - Prints up to last `k` scores. Missing player → `NOT FOUND`.  
  - Edge cases: `k<0` → `ERROR: k must be non-negative`; `k=0` prints nothing.

- `TOP_K k`  
  - Snapshot of players **with ≥1 score**, heap-sorted by `(best desc, name asc)`.  
  - Edge cases: `k<=0` → `ERROR: k must be positive`; no eligible players → `EMPTY`.

- `PRINT_ALL`  
  - Prints **all players with ≥1 score** in the same heap order. (Players with no scores are **excluded** by policy.)

- `REMOVE_PLAYER name`  
  - Deletes player and entire history; missing player → `NOT FOUND`.

- `LEN`  
  - Number of registered players (includes players with and without scores).

- `CLEAR`  
  - Removes all players and histories.

- `QUIT`  
  - Terminates immediately; lines after `QUIT` are ignored.

---

## Test Transcript
**Please see the `sampleoutput.txt` file to see a short session covering the commands and edge cases**


