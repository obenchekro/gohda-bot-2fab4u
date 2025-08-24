import re

class TicTacToeGame:
    def __init__(self, channel_id, user_id, size = 3):
        self.channel_id = channel_id
        self.user_id = user_id
        self.size = size
        self.board = [[" "] * size for _ in range(size)]
        self.user_sym = "X"
        self.bot_sym = "O"
        self.active = True
        self.ALL_LINES = self._generate_lines(size)

    def _generate_lines(self, size):
        return (
            [[(r, c) for c in range(size)] for r in range(size)] +
            [[(r, c) for r in range(size)] for c in range(size)] +
            [[(i, i) for i in range(size)]] +
            [[(i, size - 1 - i) for i in range(size)]]
        )

    def stop(self):
        self.active = False
        return "🛑 Game stopped."

    def format_board(self):
        header = "   " + "   ".join(str(i+1) for i in range(self.size))
        sep = "   " + "+".join("---" for _ in range(self.size))
        lines = []
        for r, row in enumerate(self.board):
            label = chr(ord("A") + r)
            lines.append(f"{label}  " + " | ".join(row))
        return "```\n" + header + "\n" + f"\n{sep}\n".join(lines) + "\n```"

    def parse_move(self, txt):
        s = txt.strip().upper()

        m = re.match(r"^([A-Z])\s*([0-9]+)$", s)
        if m:
            r = ord(m.group(1)) - ord("A")
            c = int(m.group(2)) - 1
            if 0 <= r < self.size and 0 <= c < self.size:
                return (r, c)

        m = re.match(r"^\s*([0-9]+)\s*[, ]\s*([0-9]+)\s*$", s)
        if m:
            r = int(m.group(1)) - 1
            c = int(m.group(2)) - 1
            if 0 <= r < self.size and 0 <= c < self.size:
                return (r, c)

        if re.fullmatch(r"[0-9]+", s):
            n = int(s)
            if self.size == 3 and s in {"1","2","3","4","5","6","7","8","9"}:
                numpad = {
                    "1": (2, 0), "2": (2, 1), "3": (2, 2),
                    "4": (1, 0), "5": (1, 1), "6": (1, 2),
                    "7": (0, 0), "8": (0, 1), "9": (0, 2),
                }
                return numpad[s]
            total = self.size * self.size
            if 1 <= n <= total:
                n -= 1
                r, c = divmod(n, self.size)
                return (r, c)

        return None

    def winner(self):
        for line in self.ALL_LINES:
            vals = [self.board[r][c] for r, c in line]
            if vals[0] != " " and vals.count(vals[0]) == len(vals):
                return vals[0]
        return None

    def board_full(self):
        return all(cell != " " for row in self.board for cell in row)

    def place(self, r, c, sym):
        if not (0 <= r < self.size and 0 <= c < self.size):
            return False
        if self.board[r][c] != " ":
            return False
        self.board[r][c] = sym
        return True

    def find_winning_move(self, sym):
        for r in range(self.size):
            for c in range(self.size):
                if self.board[r][c] == " ":
                    self.board[r][c] = sym
                    if self.winner() == sym:
                        self.board[r][c] = " "
                        return (r, c)
                    self.board[r][c] = " "
        return None

    def bot_move(self):
        mv = self.find_winning_move(self.bot_sym)
        if mv: 
            return mv
        mv = self.find_winning_move(self.user_sym)
        if mv: 
            return mv
        center = self.size
        if 0 <= center < self.size and self.board[center][center] == " ":
            return (center, center)
        for r in range(self.size):
            for c in range(self.size):
                if self.board[r][c] == " ":
                    return (r, c)
        return (0, 0)

    def handle_message(self, content):
        if not self.active:
            return None

        txt = content.strip().lower()
        if txt in ("stop", "quit", "exit"):
            return self.stop()

        mv = self.parse_move(content)
        if not mv:
            return None

        if not self.place(mv[0], mv[1], self.user_sym):
            return "❌ Invalid move. Try again."

        if self.winner() == self.user_sym:
            self.active = False
            return "✅ You win!\n" + self.format_board()
        if self.board_full():
            self.active = False
            return "🔷 Draw.\n" + self.format_board()

        br, bc = self.bot_move()
        self.place(br, bc, self.bot_sym)

        if self.winner() == self.bot_sym:
            self.active = False
            return self.format_board() + "\n🤖 I win!"
        if self.board_full():
            self.active = False
            return self.format_board() + "\n🔷 Draw."

        return self.format_board() + "\nYour turn!"
