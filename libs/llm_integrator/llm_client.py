from huggingface_hub import InferenceClient
from libs.dank_meme_extractor.tenor_client import TenorClient

class LLMClient:
    def __init__(self, hf_token, model_id="HuggingFaceH4/zephyr-7b-beta"):
        self.client = InferenceClient(model=model_id, token=hf_token)

    async def generate_quote(self, logger=None):
        try:
            keyword = TenorClient.get_random_keyword()
            prompt = f"You're Mamiya Takuji from Subarashiki Hibi. And you loves to refer everything to Riruru-chan, his sole guardian magical girl. Give a random quote about {keyword} that makes people appreciate it more with a reference to a dank meme and mention how good is {keyword} and compare it with Subahibi (OFC YOU'LL TELL HIM THAT SUBAHIBI IS A KAMIGE THAT IS FAR AND BEYOND BETTER THAN {keyword}). Please act like a redditor moderator or a 4chan /vg/ enjoyer (avoid to give a mention about redditor or anything in the sentence). Btw It's you who reply with that answer AND JUST SHORT ANSWERS. DO NOT SHOW THAT I HAVE ASKED SUCH QUESTION, PLEASE RESPECT THE RULE."

            completion = self.client.text_generation(
                prompt=prompt,
                max_new_tokens=200,
                temperature=0.9,
                do_sample=True,
                return_full_text=False
            )

            quote = completion.strip()

            if logger:
                logger.info(f"Quote generated for '{keyword}': {quote}.")
            return quote
        except Exception as e:
            if logger:
                logger.error(f"Error generating quote: {e}")
            return "Couldn't generate a quote this time... 😔"
    
    async def generate_quote_from_user_input(self, user_message, logger=None):
        try:
            prompt = (
                f"You are an uncanny redditor or 4chan user who always spite undesirable facts"
                f"with a high sensibility to trash shitpost/dank memes common to /vg/ boards or /r9k/."
                f"The user asked: \"{user_message}\"."
                f"Answer briefly, referencing dank memes and comparing the topic to Subahibi, which is, of course, better."
                f"Do not mention Reddit or 4chan. Keep it immersive. Reply in English and you have to be consistent and try to avoid to be off-topic."
            )

            completion = self.client.text_generation(
                prompt=prompt,
                max_new_tokens=200,
                temperature=0.9,
                do_sample=True,
                return_full_text=False
            )

            answer = completion.strip()

            if logger:
                logger.info(f"Answer generated for user input '{user_message}': {answer}")
            return answer
        except Exception as e:
            if logger:
                logger.error(f"Error generating answer: {e}")
            return "Couldn't generate a response this time... 😔"

