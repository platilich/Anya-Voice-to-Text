from bot.logger import logger
from groq import AsyncGroq, RateLimitError, AuthenticationError
from core.models import GroqAPIKey



class AllGroqKeysFailedError(Exception):
  """Вызывается, когда все API-ключи Groq невалидны, заблокированы или превысили лимит."""
  pass



async def recognize(file_path):
    keys = await GroqAPIKey.get_api_keys()

    if keys is None:
        logger.error('Add at least one groq key to the admin panel')
        raise AllGroqKeysFailedError("No API keys found in database")




    for key in keys:
        try:
            groq_client = AsyncGroq(api_key=key.api_key)


            logger.info('audio_recognition | recognition')


            with open(file_path, "rb") as file:
                result = await groq_client.audio.transcriptions.create(
                    file=(file_path, file.read()),
                    model="whisper-large-v3",
                    temperature=0,
                )

            return result.text



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