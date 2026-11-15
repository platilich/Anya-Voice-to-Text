from services.system_prompt import SYSTEM_PROMPT
from transcription.models import get_api_keys, get_selected_models

from google import genai
from google.genai import types


async def make_text_shorter(text: str):
    keys = await get_api_keys()
    selected_model = await get_selected_models('text')


    for key in keys:
        client = genai.Client(api_key=key)

        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=text),
                ],
            ),
        ]

        generate_content_config = types.GenerateContentConfig(
            system_instruction=[
                types.Part.from_text(text=SYSTEM_PROMPT)
            ],
            thinking_config=types.ThinkingConfig(
                thinking_level="MINIMAL",
            ),
        )

        response = client.models.generate_content(
            model=selected_model,
            contents=contents,
            config=generate_content_config,
        )


        return response.text