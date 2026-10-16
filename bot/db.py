import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from .logger import logger



class Users:
    def __init__(self):
        self.db_path = Path(__file__).resolve().parent.parent / 'db.sqlite3'


    def get_connection(self):
        return sqlite3.connect(self.db_path)



    def add_user(self, user_id, name, nickname):
        try:
            logger.info('DB | add_user')

            with self.get_connection() as conn:
                cursor = conn.cursor()


                cursor.execute(
                    'SELECT user_id FROM users_telegramuser WHERE user_id = ?',
                    (user_id,)
                )
                user = cursor.fetchone()


                if user is None:
                    created_at = datetime.now(timezone.utc).isoformat()
                    cursor.execute(
                        '''INSERT INTO users_telegramuser
                           (user_id, name, nickname, count, created_at, is_banned)
                           VALUES (?, ?, ?, ?, ?, ?)''',
                        (user_id, name, nickname, 0, created_at, 0)
                    )

                conn.commit()



        except Exception as e:
            logger.error(f'DB | error when adding a user: {e}')



    def increment_video_conversion_count(self, user_id):
        try:
            logger.info('DB | increment_video_conversion_count')
            with self.get_connection() as conn:
                cursor = conn.cursor()


                cursor.execute(
                    'UPDATE users_telegramuser SET count_video = count_video + 1 WHERE user_id = ?',
                    (user_id,)
                )


                conn.commit()


        except Exception as e:
            logger.error(f'DB | error when update count: {e}')




    def increment_recognition_count(self, user_id):
        try:
            logger.info('DB | increment_recognition_count')
            with self.get_connection() as conn:
                cursor = conn.cursor()


                cursor.execute(
                    'UPDATE users_telegramuser SET count_recognise = count_recognise + 1 WHERE user_id = ?',
                    (user_id,)
                )


                conn.commit()


        except Exception as e:
            logger.error(f'DB | error when update count: {e}')







    def is_banned(self, user_id: int) -> bool:
        try:
            logger.info('DB | is_banned')
            with self.get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    'SELECT is_banned FROM users_telegramuser WHERE user_id = ?',
                    (user_id,)
                )
                result = cursor.fetchone()

                # Если пользователь найден, берем значение поля is_banned (1 или 0)
                if result is not None:
                    return bool(result[0])

                return False

        except Exception as e:
            logger.error(f'DB | error when checking ban status: {e}')
            return False



    def get_custom_messages(self):
        try:
            logger.info('DB | get_custom_messages')


            with self.get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute('SELECT * FROM users_customizemessages')
                rows = cursor.fetchone()

                return rows

        except Exception as e:
            logger.error(f'DB | error when get_custom_messages: {e}')
            return False




    def get_api_keys(self):
        try:

            logger.info('DB | get_api_keys')


            with self.get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute('SELECT * FROM users_groqapikey')
                rows = cursor.fetchall()

                return rows


        except Exception as e:
            logger.error(f'DB | error when get_api_keys: {e}')
            return False