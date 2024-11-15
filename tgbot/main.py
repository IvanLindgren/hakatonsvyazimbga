import telebot
import json

def initconfig():
	with open('config.json', 'r') as fcc_file:
		return json.load(fcc_file)

config_data = initconfig()

bot = telebot.TeleBot(config_data["tgBotAPI"])

def MLMock(path):
# чето делает
	return 1

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.reply_to(message, "Отправь картинку")


@bot.message_handler(content_types=['photo'])
def function_name(message):
	photo = message.photo[-1]
	file_info = bot.get_file(photo.file_id)
	downloaded_file = bot.download_file(file_info.file_path)
	save_path = 'photo.jpg'
	with open(save_path, 'wb') as new_file:
		new_file.write(downloaded_file)



@bot.message_handler(func=lambda message: True)
def echo_all(message):
	bot.reply_to(message, message.text)

bot.infinity_polling()