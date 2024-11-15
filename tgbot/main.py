import telebot
import json
import matplotlib.pyplot as plt


def initconfig():
	with open('config.json', 'r') as fcc_file:
		return json.load(fcc_file)

config_data = initconfig()

bot = telebot.TeleBot(config_data["tgBotAPI"])

def MLMock(path):
# чето делает с path
	with open('impl_data.json', 'r') as fcc_file:
		return json.load(fcc_file)

def getplot(path, data):
	plt.title('Пример графика для сохранненного файла')
	plt.xlabel('Ход')
	plt.ylabel('Счет')
	for user in data:
		for name in user:
			buf = []
			for i in data[name]:
				buf.append(i)
			plt.plot([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], buf)
	plt.savefig(path)



@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.reply_to(message, "Отправь картинку")


@bot.message_handler(content_types=['photo'])
def function_name(message):
	photo = message.photo[-1]
	file_info = bot.get_file(photo.file_id)
	downloaded_file = bot.download_file(file_info.file_path)
	save_path = message.from_user.username + 'photo.jpg'
	with open(save_path, 'wb') as new_file:
		new_file.write(downloaded_file)
	data = MLMock(save_path)
	plot_path = message.from_user.username + 'plot.png'
	getplot(plot_path, data)
	plot = open(plot_path, 'rb')
	bot.send_photo(message.chat.id, plot)


bot.infinity_polling()