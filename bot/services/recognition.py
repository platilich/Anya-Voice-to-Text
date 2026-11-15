from transcription.models import get_api_keys
from google import genai
from bot.logger import logger



async def recognize(path: str):
    keys = await get_api_keys()

    for key in keys:
        client = genai.Client(
            api_key=key,
            http_options={"api_version": "v1beta"}
        )

        # 1. Загружаем файл через Files API
        audio_file = client.files.upload(file=path)

        # 2. Вызываем interactions.create с правильной структурой словаря для файла
        response = client.interactions.create(
            model="gemini-3.5-transcribe",
            input=[
                {
                    "type": "audio",
                    "uri": audio_file.uri,
                    "mime_type": audio_file.mime_type,
                }
            ],
        )

        try:
            client.files.delete(name=str(audio_file.name))

        except Exception as e:
            logger.info(f"couldn't delete file from google server: {e}")



        response = str(response.output_text)

        return response