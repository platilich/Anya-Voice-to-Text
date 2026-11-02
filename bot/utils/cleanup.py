from os import remove
from bot.logger import logger



def remove_temp_files(files):
    logger.info('removing temp files')

    for file in files:
        try:
            remove(file)

        except Exception as e:
            logger.info(f'failed remove {file}: {e}')