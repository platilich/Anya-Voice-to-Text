from groq import AsyncGroq, RateLimitError, AuthenticationError
from groq.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam


# --- for getting API keys
from core.models import GroqAPIKey


# --- other ---
from bot.services.system_prompt import SYSTEM_PROMPT
from bot.logger import logger


# --- it is triggered when all Groq API keys are unavailable ---
class AllGroqKeysFailedError(Exception):
    pass



async def make_text_shorter(text):
    # --- getting all keys from db ---
    keys = await GroqAPIKey.get_api_keys()

    # --- log this ---
    logger.info('get all api keys | make_text_shorter')


    if keys is None:
        logger.error('Add at least one groq key to the admin panel')
        raise AllGroqKeysFailedError("No API keys found in database")


    prompt = text.replace('GitHub', '')



    for key in keys:
        try:
            # --- insert the key ---
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


        # --- if problem with groq key ---
        except (RateLimitError, AuthenticationError) as e:
            logger.warning(f'key {key.api_key[:8]} failed, try next: {e}')
            continue


        # --- if something went wrong with key ---
        except Exception as e:
            logger.error(f'make_text_shorter | something wrong with key: {e}')
            continue



    logger.error('all groq keys failed')
    raise AllGroqKeysFailedError("All Groq API keys are exhausted or invalid")