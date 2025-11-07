"""
# Richard Phan
# COMP282 – Project 2: Gaming Leaderboard
# Date: 11/5/25

# Description:
#   See README file
"""
import sys

# provided by instructions
class ScoreNode:
    # LL node for storing individual scores
    __slots__ = ("value", "next")

    def __init__(self, value, next_node=None):
        self.value = value
        self.next = next_node


# given from instructions
class Player:
    # Player record with parameters name, best score, score history, and registry link.
    __slots__ = ("name", "best", "head", "next")

    def __init__(self, name):
        self.name = name
        self.best = None  # set to None bc no scores yet
        self.head = None
        self.next = None  # optional registry list link


# given from instructions
class Vector:
    # dynamic array with manual resizing
    def __init__(self, capacity=4):
        self._data = [None] * capacity
        self._size = 0
        self._capacity = capacity

    # adds item to end of vector
    def push_back(self, item):
        if self._size == self._capacity:
            self._grow()
        self._data[self._size] = item
        self._size += 1

    # get item at index
    def get(self, index):
        if index < 0 or index >= self._size:
            raise IndexError("Vector index out of range")
        return self._data[index]

    # set item at index
    def set(self, index, item):
        if index < 0 or index >= self._size:
            raise IndexError("Vector index out of range")
        self._data[index] = item

    # Swap elements at indices i and j.
    def swap(self, i, j):
        temp = self._data[i]
        self._data[i] = self._data[j]
        self._data[j] = temp

    # where length = number of elem
    def length(self):
        return self._size

    # doubles the capacity
    def _grow(self):
        new_capacity = self._capacity * 2
        new_data = [None] * new_capacity
        for i in range(self._size):
            new_data[i] = self._data[i]
        self._data = new_data
        self._capacity = new_capacity

    # optional helper for forward iteration
    def reverse(self):
        i, j = 0, self._size - 1
        while i < j:
            self.swap(i, j)
            i += 1
            j -= 1


def better(a, b):
    """
    Compare two players for heap sort ordering.
    Returns True if a should come before b
    """
    # Treat None as negative infinity
    a_best = a.best if a.best is not None else float('-inf')
    b_best = b.best if b.best is not None else float('-inf')

    if a_best != b_best:
        return a_best > b_best  # Higher score is better
    return a.name < b.name  # Lexicographic tie-breaker


def heap_sort(vec):
    """
    Sort vector of players in descending order by (best, name).
    Uses max-heap with build-heap and down-heap operations.
    """
    n = vec.length()
    if n <= 1:
        return

    # Build max-heap
    for i in range(n // 2 - 1, -1, -1):
        down_heap(vec, i, n)

    # Extract elements from heap
    for i in range(n - 1, 0, -1):
        vec.swap(0, i)
        down_heap(vec, 0, i)


def down_heap(vec, start, end):
    """
    Restore heap property from start index down to end.
    end is exclusive (heap size).
    """
    root = start
    while True:
        largest = root
        left = 2 * root + 1
        right = 2 * root + 2

        if left < end and better(vec.get(left), vec.get(largest)):
            largest = left

        if right < end and better(vec.get(right), vec.get(largest)):
            largest = right

        if largest == root:
            break

        vec.swap(root, largest)
        root = largest


# main leaderboard system
class Leaderboard:

    def __init__(self):
        self.head = None  # head of player registry LL
        self.count = 0

    # finds the player using their name
    # returns Player or None
    def find(self, name):
        current = self.head
        while current is not None:
            if current.name == name:
                return current
            current = current.next
        return None

    # add new player
    def add_player(self, name):
        # Edge case: empty name
        if not name or name.strip() == "":
            print("ERROR: Player name cannot be empty")
            return

        # Check for duplicate. Case sensitive
        if self.find(name) is not None:
            print("DUPLICATE")
            return

        new_player = Player(name)
        new_player.next = self.head
        self.head = new_player
        self.count += 1

    # add score to player history
    def add_score(self, name, score):
        player = self.find(name)
        if player is None:
            print("NOT FOUND")
            return

        # Edge case: validate score is reasonable
        # prevent integer overflow
        if score < -2147483648 or score > 2147483647:
            print("ERROR: Score out of valid range")
            return

        # Add score to front of linked list
        new_score = ScoreNode(score, player.head)
        player.head = new_score

        # Update best score
        if player.best is None or score > player.best:
            player.best = score

    # print player most recent score
    def current(self, name):
        player = self.find(name)
        if player is None:
            print("NOT FOUND")
            return

        if player.head is None:
            print(f"-> {name} | current=NONE | best=NONE")
        else:
            best_str = str(player.best) if player.best is not None else "NONE"
            print(f"-> {name} | current={player.head.value} | best={best_str}")

    # function that prints player's best score
    def best(self, name):
        player = self.find(name)
        if player is None:
            print("NOT FOUND")
            return

        best_str = str(player.best) if player.best is not None else "NONE"
        print(f"-> {name} | best={best_str}")

    # print up to k most recent scores
    def history(self, name, k):
        player = self.find(name)
        if player is None:
            print("NOT FOUND")
            return

        # Edge case: k must be non-negative
        if k < 0:
            print("ERROR: k must be non-negative")
            return

        # Edge case: k = 0 means print nothing
        if k == 0:
            return

        current = player.head
        printed = 0
        while current is not None and printed < k:
            print(f"-> {current.value}")
            current = current.next
            printed += 1

    # Print top k players by best score (max-heap compliance; best-first output)
    def top_k(self, k):
        # Edge case: k must be positive
        if k <= 0:
            print("ERROR: k must be positive")
            return

        # Create snapshot of players with scores
        snapshot = Vector()
        current = self.head
        while current is not None:
            if current.best is not None:  # Only include players with scores
                snapshot.push_back(current)
            current = current.next

        if snapshot.length() == 0:
            print("EMPTY")
            return

        # sort snapshot (max-heap heapsort leaves worst..best in indices 0..n-1)
        heap_sort(snapshot)

        # print top k (best-first): iterate from end
        limit = min(k, snapshot.length())
        rank = 1
        for i in range(snapshot.length() - 1, snapshot.length() - limit - 1, -1):
            player = snapshot.get(i)
            print(f"-> {rank}. {player.name} | best={player.best}")
            rank += 1

    # prints all players ranked by best score (best-first)
    def print_all(self):
        # create snapshot of players with scores
        snapshot = Vector()
        current = self.head
        while current is not None:
            if current.best is not None:  # only include players with scores
                snapshot.push_back(current)
            current = current.next

        if snapshot.length() == 0:
            print("EMPTY")
            return

        # sort snapshot (max-heap; leaves worst..best forward)
        heap_sort(snapshot)

        # Print all (best-first): iterate from end
        rank = 1
        for i in range(snapshot.length() - 1, -1, -1):
            player = snapshot.get(i)
            print(f"-> {rank}. {player.name} | best={player.best}")
            rank += 1

    # remove player and their history
    def remove_player(self, name):
        if self.head is None:
            print("NOT FOUND")
            return

        # Special case: removing head
        if self.head.name == name:
            self.head = self.head.next
            self.count -= 1
            return

        # Find player's predecessor
        current = self.head
        while current.next is not None:
            if current.next.name == name:
                current.next = current.next.next
                self.count -= 1
                return
            current = current.next

        print("NOT FOUND")

    # length = number of players
    def len_players(self):
        print(self.count)

    # remove all players
    def clear(self):
        self.head = None
        self.count = 0


# Parse a command line into command and arguments.
def parse_command_line(line):
    line = line.strip()

    if not line or line.startswith('#'):
        return None, None

    tokens = []
    i = 0
    while i < len(line):
        # Skip whitespace
        if line[i] == ' ' or line[i] == '\t':
            i += 1
            continue

        if line[i] == '"':
            # Find closing quote
            i += 1
            start = i
            while i < len(line) and line[i] != '"':
                i += 1
            if i < len(line):  # Found closing quote
                tokens.append(line[start:i])
                i += 1
            else:  # Unclosed quote - treat rest as token
                tokens.append(line[start:])
                break
        else:
            # Regular token
            start = i
            while i < len(line) and line[i] != ' ' and line[i] != '\t':
                i += 1
            tokens.append(line[start:i])

    if not tokens:
        return None, None

    command = tokens[0].upper()
    args = tokens[1:]
    return command, args


# main fcn
def main():
    # Edge case: exactly one argument required
    if len(sys.argv) != 2:
        print("USAGE: <program> <commands_file>")
        sys.exit(1)

    filename = sys.argv[1]

    # Edge case: file doesn't exist or can't be read
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()
    except (FileNotFoundError, PermissionError, IOError):
        # instructions requires exactly one line usage on invalid file path
        print("USAGE: <program> <commands_file>")
        sys.exit(1)

    leaderboard = Leaderboard()

    for line_num, raw_line in enumerate(lines, 1):
        try:
            stripped = raw_line.strip('\n')
            if stripped.strip() == "":
                print()
                continue
            if stripped.lstrip().startswith('#'):
                continue


            print(stripped)

            command, args = parse_command_line(stripped)
            if command is None:
                continue

            if command == "QUIT":
                break
            elif command == "ADD_PLAYER":
                # Edge case: wrong arg count
                if len(args) == 0 or len(args) > 1:
                    print("ERROR: ADD_PLAYER requires exactly 1 argument")
                    continue
                leaderboard.add_player(args[0])
            elif command == "ADD_SCORE":
                # Edge case: wrong arg count
                if len(args) != 2:
                    print("ERROR: ADD_SCORE requires exactly 2 arguments")
                    continue
                try:
                    score = int(args[1])
                    leaderboard.add_score(args[0], score)
                except ValueError:
                    # Edge case: non-integer score
                    print("ERROR: Invalid score value - must be an integer")
                except OverflowError:
                    # Edge case: score too large for int conversion
                    print("ERROR: Score value too large")
            elif command == "CURRENT":
                # Edge case: wrong arg count
                if len(args) != 1:
                    print("ERROR: CURRENT requires exactly 1 argument")
                    continue
                leaderboard.current(args[0])
            elif command == "BEST":
                # Edge case: wrong arg count
                if len(args) != 1:
                    print("ERROR: BEST requires exactly 1 argument")
                    continue
                leaderboard.best(args[0])
            elif command == "HISTORY":
                # Edge case: wrong arg count
                if len(args) != 2:
                    print("ERROR: HISTORY requires exactly 2 arguments")
                    continue
                try:
                    k = int(args[1])
                    leaderboard.history(args[0], k)
                except ValueError:
                    # Edge case: non-integer k
                    print("ERROR: Invalid k value - must be an integer")
                except OverflowError:
                    # Edge case: k too large for int conversion
                    print("ERROR: k value too large")
            elif command == "TOP_K":
                # Edge case: wrong arg count
                if len(args) != 1:
                    print("ERROR: TOP_K requires exactly 1 argument")
                    continue
                try:
                    k = int(args[0])
                    leaderboard.top_k(k)
                except ValueError:
                    # Edge case: non-integer k
                    print("ERROR: Invalid k value - must be an integer")
                except OverflowError:
                    # Edge case: k too large for int conversion
                    print("ERROR: k value too large")
            elif command == "PRINT_ALL":
                # Edge case: wrong arg count
                if len(args) > 0:
                    print("ERROR: PRINT_ALL takes no arguments")
                    continue
                leaderboard.print_all()
            elif command == "REMOVE_PLAYER":
                # Edge case: wrong arg count
                if len(args) != 1:
                    print("ERROR: REMOVE_PLAYER requires exactly 1 argument")
                    continue
                leaderboard.remove_player(args[0])
            elif command == "LEN":
                # Edge case: wrong arg count
                if len(args) > 0:
                    print("ERROR: LEN takes no arguments")
                    continue
                leaderboard.len_players()
            elif command == "CLEAR":
                # Edge case: wrong arg count
                if len(args) > 0:
                    print("ERROR: CLEAR takes no arguments")
                    continue
                leaderboard.clear()
            else:
                print(f"ERROR: Unknown command '{command}'")
        except Exception as e:
            # Catch any unexpected errors and continue processing
            print(f"ERROR: Unexpected error on line {line_num}: {str(e)}")
            continue


if __name__ == "__main__":
    main()
