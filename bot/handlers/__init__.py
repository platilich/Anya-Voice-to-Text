from bot.handlers import start, profile, donate, voice, callback


def register_all_handlers(dp):
    dp.include_router(start.router)
    dp.include_router(profile.router)
    dp.include_router(voice.router)
    dp.include_router(donate.router)
    dp.include_router(callback.router)




__all__ = [
    "register_all_handlers",
    'start',
    "profile",
    "voice",
    "donate",
    'callback'
]