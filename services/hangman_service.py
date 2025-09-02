import re
from libs.bot_games.hangman import HangmanGame

class HangmanService:
    async def handle_hangman(self, message, cleaned_msg, logger):
        if not hasattr(self, "hm_sessions"):
            self.hm_sessions = {}

        key = (message.channel.id, message.author.id)

        if cleaned_msg.lower() in ("hangman rules", "hm rules"):
            await self.post_message(
                message.channel.id,
                "**📘 Hangman Rules**\n"
                "- Guess the hidden word by proposing letters or the whole word.\n"
                "- You lose a life for each wrong guess. At max errors, you are hanged.\n"
                "- Commands:\n"
                "  • `hangman` or `hm` to start (options: `hm easy`, `hm hard`, `hm 8`).\n"
                "  • `hm hint` to get an AI hint (limited).\n"
                "  • Type a **letter** (`a`) or a **word**.\n"
                "  • `hm stop` to end the game.",
                logger
            )
            return True

        if key in self.hm_sessions and self.hm_sessions[key].active:
            if cleaned_msg.lower() in ("hangman hint", "hm hint", "hint"):
                clue = await self.hm_sessions[key].hint(self.llm_client, logger=logger)
                await self.post_message(message.channel.id, clue, logger)
                if not self.hm_sessions[key].active:
                    self.hm_sessions.pop(key, None)
                return True
            game = self.hm_sessions[key]
            reply = game.handle_message(cleaned_msg)
            await self.post_message(message.channel.id, reply, logger)
            if not game.active:
                self.hm_sessions.pop(key, None)
            return True

        m = re.match(r"^(?:hangman|hm)(?:\s+(.*))?$", cleaned_msg.strip(), flags=re.IGNORECASE)
        if m:
            args = (m.group(1) or "").strip()
            max_errors = 6
            secret = None

            if args:
                if re.fullmatch(r"\d{1,2}", args):
                    n = int(args)
                    max_errors = max(3, min(10, n))
                elif args.lower() in ("easy",):
                    max_errors = 8
                elif args.lower() in ("hard",):
                    max_errors = 5
                elif args.lower().startswith("secret "):
                    if message.guild is None:
                        secret = args[7:].strip()
                    else:
                        await self.post_message(message.channel.id, "🔒 Use `hm secret <word>` in DM only.", logger)
                        return True

            game = HangmanGame(message.channel.id, message.author.id, secret=secret, max_errors=max_errors)
            self.hm_sessions[key] = game
            await self.post_message(
                message.channel.id,
                f"🔤 **Hangman** started! (max errors: {max_errors})\n{game.format_board()}",
                logger
            )
            return True

        if cleaned_msg.lower() in ("hangman stop", "hm stop", "stop hangman"):
            game = self.hm_sessions.get(key)
            if game and game.active:
                msg = game.stop()
                self.hm_sessions.pop(key, None)
                await self.post_message(message.channel.id, msg, logger)
            else:
                await self.post_message(message.channel.id, "No active hangman game found.", logger)
            return True

        return False
