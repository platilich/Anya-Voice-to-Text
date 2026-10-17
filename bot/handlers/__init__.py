from aiogram import Dispatcher

from . import command_start, command_profile, command_get_plus, handler_voice_and_video_note, handler_video, detect_id_sticker


def register_all_handlers(dp: Dispatcher) -> None:
    dp.include_router(command_start.router)
    dp.include_router(command_profile.router)
    dp.include_router(command_get_plus.router)
    dp.include_router(handler_voice_and_video_note.router)
    # dp.include_router(handler_video.router)
    dp.include_router(detect_id_sticker.router)




__all__ = [
    "register_all_handlers",
    'command_start',
    "command_profile",
    "command_get_plus",
    "handler_voice_and_video_note",
    #'handler_video',
    'detect_id_sticker'
]