import telebot

bot = telebot.TeleBot("")

def MLMock(path):
# чето делает
	return 1

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.reply_to(message, "Отправь картинку")


@bot.message_handler(content_types=['photo'])
def function_name(message):
	bot.reply_to(message, "Картинка")


@bot.message_handler(func=lambda message: True)
def echo_all(message):
	bot.reply_to(message, message.text)

bot.infinity_polling()