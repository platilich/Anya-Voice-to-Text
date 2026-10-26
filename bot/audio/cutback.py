from bot.logger import logger
from groq import AsyncGroq, RateLimitError, AuthenticationError
from core.models import GroqAPIKey
from groq.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam

from system_prompt import SYSTEM_PROMPT



# --- it is triggered when all Groq API keys are unavailable ---
class AllGroqKeysFailedError(Exception):
    pass



async def make_text_shorter(text):
    keys = await GroqAPIKey.get_api_keys()


    if keys is None:
        logger.error('Add at least one groq key to the admin panel')
        raise AllGroqKeysFailedError("No API keys found in database")



    prompt = text.replace('GitHub', '')



    for key in keys:
        try:

            client = AsyncGroq(api_key=key.api_key)


            completion = await client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    ChatCompletionSystemMessageParam(
                        role="system",
                        content=SYSTEM_PROMPT
                    ),

                    ChatCompletionUserMessageParam(
                        role="user",
                        content=f"<text>{prompt}</text>"
                    )
                ],
                temperature=0,
                max_completion_tokens=2048,
                reasoning_effort="low",
                top_p=1
            )

            response_text = completion.choices[0].message.content
            return response_text



        except (RateLimitError, AuthenticationError) as e:
            logger.warning(
                f"Groq key {key.api_key[:8]}... failed: {e}. Trying next key..."
            )
            continue



        except Exception as e:
            logger.error(f"audio_recognition | unexpected error with key: {e}")
            continue



    logger.error("Error: All Groq API keys failed or rate-limited.")
    raise AllGroqKeysFailedError("All Groq API keys are exhausted or invalid")