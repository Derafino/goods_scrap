
import configparser
config = configparser.ConfigParser()
config.read("settings.ini")

TelegramToken = config["Telegram"]["TOKEN"]

ChatID = config["Telegram"]["CHAT_ID"]

ATBshops = {}
SILPOshops = {}
Chats = {}

DATABASE_NAME = '/goods.db'



