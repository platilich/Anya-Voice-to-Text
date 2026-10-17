from bot.logger import logger
from groq import AsyncGroq, RateLimitError, AuthenticationError
from users.models import GroqAPIKey



async def recognize(file_path):
    keys = await GroqAPIKey.get_api_keys()

    if keys is None:
        return 'Add at least one groq key to the admin panel'


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


        except (RateLimitError,  AuthenticationError):
            continue


        except Exception as e:
            logger.error(f'audio_recognition | error: {e}')
            continue




    return 'Error problem with key'