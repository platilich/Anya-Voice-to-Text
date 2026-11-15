from moviepy import VideoFileClip
from bot.logger import  logger


async def conver_to_ogg(file_path):
    try:
        video = VideoFileClip(file_path)

        new_path = file_path.replace('.mp4', '.ogg')
        video.audio.write_audiofile(new_path)


        video.close()


        return new_path



    except Exception as e:
        logger.error(f'an error occurred during conversion: {e}')
        return False