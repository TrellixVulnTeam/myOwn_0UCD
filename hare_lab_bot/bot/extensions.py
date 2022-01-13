import sqlite3
import files
import yaml
import logging

# set logging level
logging.basicConfig(filename=files.system_log, format='%(levelname)s:%(name)s:%(asctime)s:%(message)s',
                    datefmt='%d.%m.%Y %I:%M:%S %p', level=logging.INFO)


# класс по настройке бота
class Settings:
    def __init__(self):
        self.file_settings = open(files.settings, 'r')  # открываем файл для чтения
        self.settings = yaml.safe_load(self.file_settings)
        self.time_zone = str(self.settings['Settings']['TimeZone'])
        self.channel_name = str(self.settings['Settings']['ChannelName'])
        self.channel_id = str(self.settings['Settings']['ChannelID'])
        self.threshold_xp = int(self.settings['Settings']['ThresholdXP'])
        self.file_settings.close()

        con = sqlite3.connect(files.main_db)
        cursor = con.cursor()
        cursor.execute("SELECT phrase, phrase_text, phrase_text_entities FROM phrases "
                       "WHERE phrase = 'help_text';")
        for phrase, phrase_text, phrase_text_entities in cursor.fetchall():
            self.help_text = phrase_text
            self.help_text_entities = phrase_text_entities
        logging.info('Help phrase is got')

        cursor.execute("SELECT phrase, phrase_text, phrase_text_entities FROM phrases "
                       "WHERE phrase = 'footer_text';")
        for phrase, phrase_text, phrase_text_entities in cursor.fetchall():
            self.footer_text = phrase_text
            self.footer_text_entities = phrase_text_entities
        logging.info('Footer phrase is got')

        con.close()

        self.url_csv = f'https://combot.org/c/{self.channel_id}/chat_users/v2?csv=yes&limit=3000&skip=0'
        self.url_one_time_link = ''
        self.session = None

    def __enter__(self):  # обработчик входа в контекстный менеджер
        self.file_token = open(files.token, 'r')  # открываем файл для чтения
        self.TOKEN = yaml.safe_load(self.file_token)
        logging.info('Token was set')
        return self.TOKEN['TOKEN']

    def __exit__(self, exc_type, exc_val, exc_tb):  # обработчик выхода из контекстного менеджера
        self.file_token.close()


# класс поста (используется при создании постов и редактировании, как хранилище данных до записи в базу)
class Post:
    def __init__(self):
        self.author_id: int = 0
        self.author_name: str = ''
        self.post_name: str = ''
        self.post_date: str = ''
        self.post_desc: str = ''
        self.what_needs: str = ''
        self.hashtags: str = ''
        self.pic_post: str = ''
        self.name_entities: dict = {}
        self.desc_entities: dict = {}
        self.date_entities: dict = {}
        self.what_needs_entities: dict = {}
        self.status: int = 0
        self.message_id: int = 0
