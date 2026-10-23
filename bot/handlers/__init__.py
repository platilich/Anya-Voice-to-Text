from aiogram import Dispatcher

from . import start, profile, get_plus, on_voice


def register_all_handlers(dp: Dispatcher) -> None:
    dp.include_router(start.router)
    dp.include_router(profile.router)
    dp.include_router(on_voice.router)
    dp.include_router(get_plus.router)




__all__ = [
    "register_all_handlers",
    'start',
    "profile",
    "on_voice",
    "get_plus"
]