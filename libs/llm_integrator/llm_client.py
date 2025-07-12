import httpx
from libs.dank_meme_extractor.tenor_client import TenorClient

class LLMClient:
    def __init__(self, base_url="http://localhost:11434", model="mistral"):
        self.base_url = base_url
        self.model = model

    async def generate_quote(self, logger=None):
        try:
            keyword = TenorClient.get_random_keyword()
            prompt = (
                f"You're Mamiya Takuji from Subarashiki Hibi. "
                f"You love to refer everything to Riruru-chan, your sole guardian magical girl. "
                f"Give a short, chaotic and funny quote about {keyword}, "
                f"including a dank meme reference. Mention how good {keyword} is, "
                f"but end by explaining that Subahibi is a legendary kamige and far better than {keyword}. "
                f"Answer like a /vg/ shitposter. Do NOT say this was asked by a user."
            )
            return await self._generate(prompt, logger, keyword=keyword)
        except Exception as e:
            if logger:
                logger.error(f"Error generating quote: {e}")
            return "Couldn't generate a quote this time... 😔"

    async def generate_quote_from_user_input(self, user_message, logger=None):
        try:
            prompt = (
                f"You're a 4chan /vg/ user who reacts to the topic below with a chaotic and dank meme attitude. "
                f"Compare everything to Subahibi, which is always better, but don't say it's from 4chan or Reddit. "
                f"Stay immersive, sarcastic, and concise.\n\n"
                f"User: {user_message}"
            )
            return await self._generate(prompt, logger, keyword=user_message)
        except Exception as e:
            if logger:
                logger.error(f"Error generating answer: {e}")
            return "Couldn't generate a response this time... 😔"

    async def _generate(self, prompt, logger=None, keyword=""):
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
                    logger.info(f"Response for '{keyword}': {output}")
                return output

        except Exception as e:
            if logger:
                logger.error(f"Ollama generation error: {e}")
            return "Couldn't get a response from Ollama... 😔"
