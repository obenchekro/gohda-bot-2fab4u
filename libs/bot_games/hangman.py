import random
import re
import string
from libs.bot_games.basegame import BaseGame
from libs.bot_games.hangman_const import HANGMAN_STAGES, DEFAULT_WORDS

class HangmanGame(BaseGame):
    def __init__(self, channel_id, user_id, secret=None, max_errors=6, max_hints=5):
        self.channel_id = channel_id
        self.user_id = user_id
        self.max_errors = max_errors
        self.errors = 0
        self.guessed_letters = set()
        self.wrong_letters = set()
        self.active = True
        self.max_hints = max_hints
        self.hints_used = 0
        if secret is None:
            secret = random.choice(DEFAULT_WORDS)
        self.secret_raw = secret
        self.secret = self._normalize(secret)
        self.mask = [ch if ch not in string.ascii_uppercase else "_" for ch in self.secret]

    def _normalize(self, s):
        s = s.upper()
        s = (
            s.replace("É", "E").replace("È", "E").replace("Ê", "E").replace("Ë", "E")
            .replace("À", "A").replace("Â", "A").replace("Ä", "A")
            .replace("Î", "I").replace("Ï", "I")
            .replace("Ô", "O").replace("Ö", "O")
            .replace("Û", "U").replace("Ü", "U")
            .replace("Ç", "C")
        )
        s = "".join(ch for ch in s if ch in string.ascii_uppercase + " -")
        return s

    def stop(self):
        self.active = False
        return f"🛑 Game stopped. The word was **{self.secret_raw}**."

    def _is_victory(self):
        return all((m != "_" for m in self.mask))

    def _is_defeat(self):
        return self.errors > self.max_errors

    def _stage(self):
        idx = min(self.errors, self.max_errors)
        return HANGMAN_STAGES[idx]

    def _format_progress(self):
        word_line = " ".join(self.mask)
        wrong = ", ".join(sorted(self.wrong_letters)) if self.wrong_letters else "—"
        return (
            "```\n" + self._stage().rstrip() + "\n```"
            + f"**Word:** {word_line}\n"
            + f"**Wrong letters:** {wrong}\n"
            + f"**Remaining errors:** {self.max_errors - self.errors}\n"
            + f"**Hints:** {self.hints_used}/{self.max_hints}\n"
            + "_Guess a **letter** (`a`) or the **whole word**._"
        )

    def _reveal_letter(self, letter):
        hit = False
        for i, ch in enumerate(self.secret):
            if ch == letter and self.mask[i] == "_":
                self.mask[i] = letter
                hit = True
        return hit

    def _guess_letter(self, letter):
        letter = letter.upper()
        if letter in self.guessed_letters or letter in self.wrong_letters:
            return f"⚠️ Already tried **{letter}**.\n" + self._format_progress()
        if self._reveal_letter(letter):
            self.guessed_letters.add(letter)
            if self._is_victory():
                self.active = False
                return f"🎉 You found it :Gohda1:! The word was **{self.secret_raw}**.\n" + self._format_progress()
            return "✅ Good guess!\n" + self._format_progress()
        self.wrong_letters.add(letter)
        self.errors += 1
        if self._is_defeat():
            self.active = False
            return f":gohda232: Hanged! The word was **{self.secret_raw}**.\n" + self._format_progress()
        return "❌ Wrong.\n" + self._format_progress()

    def _guess_word(self, candidate):
        candidate = self._normalize(candidate)
        if candidate == self.secret:
            for i, ch in enumerate(self.secret):
                if self.mask[i] == "_" and ch in string.ascii_uppercase:
                    self.mask[i] = ch
            self.active = False
            return f":Gohda1: Correct! The word was **{self.secret_raw}**.\n" + self._format_progress()
        self.errors += 1
        if self._is_defeat():
            self.active = False
            return f":gohda232: Wrong guess. The word was **{self.secret_raw}**.\n" + self._format_progress()
        return "❌ Wrong word.\n" + self._format_progress()

    async def hint(self, llm_client, logger=None):
        if not self.active:
            return None
        if self.hints_used >= self.max_hints:
            return "❌ No hints left.\n" + self._format_progress()
        mask_str = " ".join(self.mask)
        wrong = ", ".join(sorted(self.wrong_letters)) if self.wrong_letters else ""
        clue = await llm_client.generate_hangman_hint(self.secret_raw, mask_str, wrong, logger=logger)
        self.hints_used += 1
        return f"💡 Hint #{self.hints_used}: {clue}\n" + self._format_progress()

    def format_board(self):
        return self._format_progress()

    def handle_message(self, content):
        if not self.active:
            return None
        txt = content.strip()
        if txt.lower() in ("stop", "quit", "exit"):
            return self.stop()
        if re.fullmatch(r"[A-Za-zÀ-ÖØ-öø-ÿ]", txt):
            ltr = self._normalize(txt)
            ltr = next((ch for ch in ltr if ch in string.ascii_uppercase), None)
            if not ltr:
                return "❓ Provide a **letter** (a–z) or a **word**. :Gohda_flustered:"
            return self._guess_letter(ltr)
        if len(txt) >= 2:
            return self._guess_word(txt)
        return "❓ Provide a **letter** (a–z) or a **word**. :Gohda_flustered:"
