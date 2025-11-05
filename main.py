#add error handling for mistyped file name: commands.tx
#Richard Phan

import sys


class ScoreNode:
    """Linked list node for storing individual scores."""
    __slots__ = ("value", "next")

    def __init__(self, value, next_node=None):
        self.value = value
        self.next = next_node


class Player:
    """Player record with name, best score, score history, and registry link."""
    __slots__ = ("name", "best", "head", "next")

    def __init__(self, name):
        self.name = name
        self.best = None  # None represents no scores yet
        self.head = None  # Head of score history linked list
        self.next = None  # Next player in registry linked list


class Vector:
    """Dynamic array with manual resizing."""

    def __init__(self, capacity=4):
        self._data = [None] * capacity
        self._size = 0
        self._capacity = capacity

    def push_back(self, item):
        """Add item to end of vector."""
        if self._size == self._capacity:
            self._grow()
        self._data[self._size] = item
        self._size += 1

    def get(self, index):
        """Get item at index."""
        if index < 0 or index >= self._size:
            raise IndexError("Vector index out of range")
        return self._data[index]

    def set(self, index, item):
        """Set item at index."""
        if index < 0 or index >= self._size:
            raise IndexError("Vector index out of range")
        self._data[index] = item

    def swap(self, i, j):
        """Swap elements at indices i and j."""
        temp = self._data[i]
        self._data[i] = self._data[j]
        self._data[j] = temp

    def length(self):
        """Return number of elements."""
        return self._size

    def _grow(self):
        """Double the capacity."""
        new_capacity = self._capacity * 2
        new_data = [None] * new_capacity
        for i in range(self._size):
            new_data[i] = self._data[i]
        self._data = new_data
        self._capacity = new_capacity


def better(a, b):
    """
    Compare two players for heap sort ordering.
    Returns True if a should rank higher than b.
    Comparison: best score descending, then name ascending (tie-breaker).
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


class Leaderboard:
    """Main leaderboard system."""

    def __init__(self):
        self.head = None  # Head of player registry linked list
        self.count = 0

    def find(self, name):
        """Find player by name. Returns Player or None."""
        current = self.head
        while current is not None:
            if current.name == name:
                return current
            current = current.next
        return None

    def add_player(self, name):
        """Add a new player."""
        # Edge case: empty name
        if not name or name.strip() == "":
            print("ERROR: Player name cannot be empty")
            return

        # Check for duplicate (case-sensitive as per spec)
        if self.find(name) is not None:
            print("DUPLICATE")
            return

        new_player = Player(name)
        new_player.next = self.head
        self.head = new_player
        self.count += 1

    def add_score(self, name, score):
        """Add a score to a player's history."""
        player = self.find(name)
        if player is None:
            print("NOT FOUND")
            return

        # Edge case: validate score is reasonable
        # Prevent integer overflow issues
        if score < -2147483648 or score > 2147483647:
            print("ERROR: Score out of valid range")
            return

        # Add score to front of linked list
        new_score = ScoreNode(score, player.head)
        player.head = new_score

        # Update best score
        if player.best is None or score > player.best:
            player.best = score

    def current(self, name):
        """Print player's most recent score."""
        player = self.find(name)
        if player is None:
            print("NOT FOUND")
            return

        if player.head is None:
            print(f"-> {name} | current=NONE | best=NONE")
        else:
            best_str = str(player.best) if player.best is not None else "NONE"
            print(f"-> {name} | current={player.head.value} | best={best_str}")

    def best(self, name):
        """Print player's best score."""
        player = self.find(name)
        if player is None:
            print("NOT FOUND")
            return

        best_str = str(player.best) if player.best is not None else "NONE"
        print(f"-> {name} | best={best_str}")

    def history(self, name, k):
        """Print up to k most recent scores."""
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

    def top_k(self, k):
        """Print top k players by best score."""
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

        # Sort snapshot
        heap_sort(snapshot)

        # Print top k (or all if k > length)
        limit = min(k, snapshot.length())
        for i in range(limit):
            player = snapshot.get(i)
            print(f"-> {i + 1}. {player.name} | best={player.best}")

    def print_all(self):
        """Print all players sorted by best score."""
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

        # Sort snapshot
        heap_sort(snapshot)

        # Print all
        for i in range(snapshot.length()):
            player = snapshot.get(i)
            print(f"-> {i + 1}. {player.name} | best={player.best}")

    def remove_player(self, name):
        """Remove a player and their history."""
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

    def len_players(self):
        """Print number of players."""
        print(self.count)

    def clear(self):
        """Remove all players."""
        self.head = None
        self.count = 0


def parse_command_line(line):
    """Parse a command line into command and arguments."""
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


def main():
    """Main entry point."""
    # Edge case: no arguments provided
    if len(sys.argv) != 2:
        print("USAGE: <program> <commands_file>")
        sys.exit(1)

    filename = sys.argv[1]

    # Edge case: file doesn't exist or can't be read
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print("USAGE: <program> <commands_file>")
        sys.exit(1)
    except PermissionError:
        print("USAGE: <program> <commands_file>")
        sys.exit(1)
    except IOError:
        print("USAGE: <program> <commands_file>")
        sys.exit(1)

    leaderboard = Leaderboard()

    for line_num, line in enumerate(lines, 1):
        try:
            command, args = parse_command_line(line)

            if command is None:
                continue

            if command == "QUIT":
                break
            elif command == "ADD_PLAYER":
                if len(args) == 0:
                    print("ERROR: ADD_PLAYER requires exactly 1 argument")
                    continue
                elif len(args) > 1:
                    print("ERROR: ADD_PLAYER requires exactly 1 argument")
                    continue
                leaderboard.add_player(args[0])
            elif command == "ADD_SCORE":
                if len(args) < 2:
                    print("ERROR: ADD_SCORE requires exactly 2 arguments")
                    continue
                elif len(args) > 2:
                    print("ERROR: ADD_SCORE requires exactly 2 arguments")
                    continue
                try:
                    score = int(args[1])
                    leaderboard.add_score(args[0], score)
                except ValueError:
                    print("ERROR: Invalid score value - must be an integer")
                except OverflowError:
                    print("ERROR: Score value too large")
            elif command == "CURRENT":
                if len(args) == 0:
                    print("ERROR: CURRENT requires exactly 1 argument")
                    continue
                elif len(args) > 1:
                    print("ERROR: CURRENT requires exactly 1 argument")
                    continue
                leaderboard.current(args[0])
            elif command == "BEST":
                if len(args) == 0:
                    print("ERROR: BEST requires exactly 1 argument")
                    continue
                elif len(args) > 1:
                    print("ERROR: BEST requires exactly 1 argument")
                    continue
                leaderboard.best(args[0])
            elif command == "HISTORY":
                if len(args) < 2:
                    print("ERROR: HISTORY requires exactly 2 arguments")
                    continue
                elif len(args) > 2:
                    print("ERROR: HISTORY requires exactly 2 arguments")
                    continue
                try:
                    k = int(args[1])
                    leaderboard.history(args[0], k)
                except ValueError:
                    print("ERROR: Invalid k value - must be an integer")
                except OverflowError:
                    print("ERROR: k value too large")
            elif command == "TOP_K":
                if len(args) == 0:
                    print("ERROR: TOP_K requires exactly 1 argument")
                    continue
                elif len(args) > 1:
                    print("ERROR: TOP_K requires exactly 1 argument")
                    continue
                try:
                    k = int(args[0])
                    leaderboard.top_k(k)
                except ValueError:
                    print("ERROR: Invalid k value - must be an integer")
                except OverflowError:
                    print("ERROR: k value too large")
            elif command == "PRINT_ALL":
                if len(args) > 0:
                    print("ERROR: PRINT_ALL takes no arguments")
                    continue
                leaderboard.print_all()
            elif command == "REMOVE_PLAYER":
                if len(args) == 0:
                    print("ERROR: REMOVE_PLAYER requires exactly 1 argument")
                    continue
                elif len(args) > 1:
                    print("ERROR: REMOVE_PLAYER requires exactly 1 argument")
                    continue
                leaderboard.remove_player(args[0])
            elif command == "LEN":
                if len(args) > 0:
                    print("ERROR: LEN takes no arguments")
                    continue
                leaderboard.len_players()
            elif command == "CLEAR":
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