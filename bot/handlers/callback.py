from aiogram import Router, F
from aiogram.types import CallbackQuery


from bot.services.cutback import make_text_shorter

import html

router = Router(name='callback')



@router.callback_query(F.data == "summarize")
async def handle_cut_back(callback: CallbackQuery):
    message_text = callback.message.text


    # --- remove button ---
    await callback.message.edit_reply_markup(reply_markup=None)

    # --- answer on callback ---
    await callback.answer()


    # --- calling function, which make text shorter and send result ---
    short_text = await make_text_shorter(message_text)

    response = (
        f'<blockquote>{html.escape(short_text)}</blockquote>'
       '\n\n<a href="https://github.com/platilich/anya-voice-to-text"><b>GitHub</b></a>'
    )

    await callback.message.answer(
        text=response,
        parse_mode='HTML',
        disable_web_page_preview=True

    )