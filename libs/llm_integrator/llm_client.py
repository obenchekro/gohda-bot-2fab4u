import httpx
from libs.dank_meme_extractor.tenor_client import TenorClient

class LLMClient:
    def __init__(self, base_url="http://localhost:11434", model="mistral", bot_id=None):
        self.base_url = base_url
        self.model = model
        self.bot_id = bot_id

    async def generate_quote(self, bot_type, logger=None):
        try:
            keyword = TenorClient.get_random_keyword()
            prompt = (
                f"You're a disgusting scumbag coomer. "
                f"who simps over any kind of person (see the emasculated men in OF or MYM). "
                f"Give a short, chaotic and funny quote about {keyword}, "
                f"Answer like a /h/ shitposter. Do NOT say this was asked by a user."
            ) if bot_type == "zaim" else (
                f"You're Mamiya Takuji from Subarashiki Hibi. "
                f"You love to refer everything to Riruru-chan, your sole guardian magical girl. "
                f"Give a short, chaotic and funny quote about {keyword}, "
                f"including a dank meme reference. Mention how good {keyword} is, "
                f"but end by explaining that Subahibi is a legendary kamige and far better than {keyword}. "
                f"Answer like a /vg/ shitposter. Do NOT say this was asked by a user."
            ) 
            return await self._generate(prompt, bot_type, logger, keyword=keyword)
        except Exception as e:
            if logger:
                logger.error(f"Error generating quote: {e}")
            return "Couldn't generate a quote this time... 😔"

    async def generate_quote_from_user_input(self, bot_type, user_message, logger=None):
        try:
            prompt = (
                f"You're a disgusting scumbag coomer 4chan /h/ user who reacts to the topic below with a chaotic and dank meme attitude. "
                f"who simps over any kind of person (see the emasculated men in OF or MYM). "
                f"Stay immersive, despicable, and outrageous when you answer to user response which is actually: \"{user_message}\".\n\n"
                f"Answer like a /h/ shitposter. Do NOT say this was asked by a user."
                f"User: {user_message}"
            ) if bot_type == "zaim" else (
                f"You're a 4chan /vg/ user who reacts to the topic below with a chaotic and dank meme attitude. "
                f"Compare everything to Subahibi, which is always better, but don't say it's from 4chan or Reddit. "
                f"Stay immersive, sarcastic, and concise.\n\n"
                f"User: {user_message}"
            )

            return await self._generate(prompt, bot_type, logger, keyword=user_message)
        except Exception as e:
            if logger:
                logger.error(f"Error generating answer: {e}")
            return "Couldn't generate a response this time... 😔"
        
    async def generate_roast(self, from_bot, target_mention, logger=None):
        if hasattr(self, "bot_id"):
            try:
                target_id = int(target_mention.strip("<@!>"))
                if target_id == self.bot_id:
                    if logger:
                        logger.warning(f"{from_bot} tried to roast itself. Ignoring.")
            except ValueError:
                if logger:
                    logger.warning(f"Invalid target_mention format: {target_mention}")
        
        if from_bot == "zaim":
            prompt = (
                f"You're Gohda, a smug, sarcastic, elitist bot in an insult battle. "
                f"Your target is {target_mention}. "
                f"Write a short, brutal roast. Never insult yourself. "
                f"Use a passive-aggressive, intellectual tone. Your goal is to make {target_mention} look pathetic, like they're the human version of Internet Explorer. "
                f"But if the target {target_mention} is different from {self.bot_id} then just roast the fucking Zaim AND DO NOT PING {target_mention}"
            )
        else:
            prompt = (
                f"You're Zaim, a chaotic, meme-fueled shitposter from 4chan, locked in a roast battle. "
                f"Your target is {target_mention}. "
                f"Respond with pure internet chaos and dark humor, like a Twitter reply guy hopped up on Monster Energy. "
                f"Never insult yourself. Always punch hard and direct at {target_mention}. Include 1~2 dank memes or VN/anime references."
                f"But if the target {target_mention} is different from {self.bot_id} then just roast the fucking Gohda. "
            )

        return await self._generate(prompt, bot_type=from_bot, logger=logger)


    async def _generate(self, prompt, bot_type, logger=None, keyword=""):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False
                    },
                    timeout=60
                )
                response.raise_for_status()
                data = response.json()
                output = data.get("response", "").strip()

                if logger:
                    logger.info(f"Response as {bot_type} for '{keyword}': {output}")
                return output

        except Exception as e:
            if logger:
                logger.error(f"Ollama generation error: {e}")
            return "Couldn't get a response from Ollama... 😔"
