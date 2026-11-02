from groq import AsyncGroq, RateLimitError, AuthenticationError
from core.models import GroqAPIKey
from bot.logger import logger



# --- it is triggered when all Groq API keys are unavailable ---
class AllGroqKeysFailedError(Exception):
    pass



async def recognize(file_path):
    # --- getting api keys from db ---
    keys = await GroqAPIKey.get_api_keys()

    # --- log this ---
    logger.info('attempt to get api keys | recognize')

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
            logger.warning(f'key {key.api_key[:8]} failed, try next: {e}')
            continue



        except OSError:
            # The file was never saved, or the disk read failed. That is not
            # a bad key, so do not walk the rest of the key list.
            raise

        except Exception as e:
            logger.error(f'recognize | something wrong with key: {e}')
            continue



    logger.error('all groq keys failed')
    raise AllGroqKeysFailedError("All Groq API keys are exhausted or invalid")