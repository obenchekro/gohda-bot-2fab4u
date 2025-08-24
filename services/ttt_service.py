import re
from libs.bot_games.tic_tac_toe import TicTacToeGame

class TTTService:
    async def handle_ttt(self, message, cleaned_msg, logger):
        if not hasattr(self, "ttt_sessions"):
            self.ttt_sessions = {}

        key = (message.channel.id, message.author.id)
        MIN_SIZE = 3
        MAX_SIZE = 10

        if cleaned_msg.lower() in ("ttt rules", "tic tac toe rules", "tictactoe rules"):
            await self.post_message(
                message.channel.id,
                "**📘 Tic-Tac-Toe Rules**\n"
                "- The game is played on an N×N board (default 3×3).\n"
                "- You play with ❌, the bot plays with ⭕.\n"
                "- Players take turns placing their symbol.\n"
                "- First to align N symbols in a row, column, or diagonal wins.\n"
                "- If the board fills with no winner, it’s a draw.\n"
                "- To play: type `A1`, `2 3`, or `5` (for 3×3).\n"
                "- Type `stop` to quit anytime.",
                logger
            )
            return True

        if key in self.ttt_sessions and self.ttt_sessions[key].active:
            game = self.ttt_sessions[key]
            reply = game.handle_message(cleaned_msg)
            if reply is None:
                await self.post_message(
                    message.channel.id,
                    "❓ Not a move. Examples: `A1`, `2 3`, `5` (3×3 numpad), or `stop`.",
                    logger
                )
                return True
            await self.post_message(message.channel.id, reply, logger)
            if not game.active:
                self.ttt_sessions.pop(key, None)
            return True

        m = re.match(r"^(?:ttt|ttt\s+start|tic\s*tac\s*toe|tictactoe)(?:\s+(.*))?$", cleaned_msg.strip(), flags=re.IGNORECASE)
        if m:
            args = (m.group(1) or "").strip()
            size = None
            hint = ""

            if not args:
                size = 3
                hint = f"(defaulting to {size}x{size}; you can start with `ttt 5` or `ttt 4x4`)"
            else:
                m2 = re.match(r"^(\d{1,2})(?:\s*[xX]\s*(\d{1,2}))?$", args)
                if not m2:
                    await self.post_message(
                        message.channel.id,
                        f"❌ Invalid board size. Use `ttt N` or `ttt NxN` (min {MIN_SIZE}, max {MAX_SIZE}).",
                        logger
                    )
                    return True
                n1 = int(m2.group(1))
                n2 = int(m2.group(2)) if m2.group(2) else n1
                if n1 != n2:
                    await self.post_message(message.channel.id, "❌ Only square boards are supported (e.g., `ttt 5` or `ttt 5x5`).", logger)
                    return True
                if not (MIN_SIZE <= n1 <= MAX_SIZE):
                    await self.post_message(message.channel.id, f"❌ Size out of range. Allowed: {MIN_SIZE}–{MAX_SIZE}.", logger)
                    return True
                size = n1

            game = TicTacToeGame(message.channel.id, message.author.id, size=size)
            self.ttt_sessions[key] = game
            await self.post_message(
                message.channel.id,
                f"🎮 Tic-Tac-Toe {size}x{size} started! {hint}\n{game.format_board()}\nYour turn! (Examples: `A1`, `5 2`, or `stop`)",
                logger
            )
            return True

        if cleaned_msg.lower() in ("ttt stop", "stop ttt", "tictactoe stop"):
            game = self.ttt_sessions.get(key)
            if game and game.active:
                msg = game.stop()
                self.ttt_sessions.pop(key, None)
                await self.post_message(message.channel.id, msg, logger)
            else:
                await self.post_message(message.channel.id, "No active game found.", logger)
            return True

        return False