from aiogram import Dispatcher

from . import start, profile, get_plus, voice, callback


def register_all_handlers(dp: Dispatcher) -> None:
    dp.include_router(start.router)
    dp.include_router(profile.router)
    dp.include_router(voice.router)
    dp.include_router(get_plus.router)
    dp.include_router(callback.router)




__all__ = [
    "register_all_handlers",
    'start',
    "profile",
    "voice",
    "get_plus",
    'callback'
]