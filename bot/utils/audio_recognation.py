from bot.logger import logger
from groq import Groq
from dotenv import load_dotenv
import os
from pathlib import Path




BASE_DIR = Path(__file__).resolve().parent.parent.parent
dotenv_path = BASE_DIR / '.env'

load_dotenv(dotenv_path)






KEY = os.getenv('API_KEY')



groq_client = Groq(api_key=KEY)


def transcription(file_path):
    try:
        logger.info('audio_recognition | recognition')


        with open(file_path, "rb") as file:
            transcription = groq_client.audio.transcriptions.create(
                file=(file_path, file.read()),
                model="whisper-large-v3-turbo",
                temperature=0,
                response_format="verbose_json",
            )



        return transcription.text


    except Exception as e:
        logger.error(f'audio_recognition | error: {e}')


