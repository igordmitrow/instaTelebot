import instabot
import telebot
import ast

insta = instabot.Bot(message_delay=0)
insta.login()
bot = telebot.TeleBot('TOKEN')
yourId = 23743267
keyboard = telebot.types.ReplyKeyboardMarkup(True,True)
keyboard.row('Подивитися всі повідомлення', 'Подивитися нові повідомлення')
currentPage = 1
sendUsername = ''


def showAllMsg():
	insta.api.get_inbox_v2()
	data = insta.last_json["inbox"]["threads"]
	ret = []
	for item in data:
		user_id = str(item["inviter"]["pk"])
		ret.append(item["users"][0]['username'])
	return ret

def makeKeyboard():
	global currentPage
	username = showAllMsg()
	username = username[(currentPage-1)*10:currentPage*10]
	markup = telebot.types.InlineKeyboardMarkup()
	for user in username:
	    		button = telebot.types.InlineKeyboardButton(text=user, callback_data="['send','" + user + "']")
	    		markup.add(button)
	prevP = telebot.types.InlineKeyboardButton(text='<', callback_data='prevPage' )
	nextP = telebot.types.InlineKeyboardButton(text='>', callback_data='nextPage')
	markup.add(prevP)
	markup.add(nextP)
	return markup

def process_text_step(message):
	try:
		chat_id = message.chat.id
		text = message.text
		insta.send_message(text,insta.get_user_id_from_username(sendUsername))
	except Exception as e:
		bot.reply_to(message,'ops')

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привет', reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
	global currentPage
	if (call.data.startswith("['send'")):
		global sendUsername
		sendUsername = ast.literal_eval(call.data)[1]
		msg = bot.send_message(call.message.chat.id, "Напишіть повідомлення, яке потрібно відправити " + sendUsername)
		bot.register_next_step_handler(msg, process_text_step)
	elif call.data == 'prevPage':
		if currentPage > 1:
			currentPage -= 1
			bot.edit_message_text(chat_id=call.message.chat.id,
                          text="Виберіть кому написати повідомлення", message_id=call.message.message_id,
                          reply_markup=makeKeyboard())
	elif call.data == 'nextPage':
		if currentPage < 2:
			currentPage += 1
			print(currentPage)
			bot.edit_message_text(chat_id=call.message.chat.id,
                          text="Виберіть кому написати повідомлення", message_id=call.message.message_id,
                          reply_markup=makeKeyboard())


@bot.message_handler(content_types=['text'])
def send_text(message):
	global yourId
    if message.text.lower() == 'подивитися всі повідомлення':
    	if message.from_user.id == yourId:
    		markup = makeKeyboard()
    		bot.send_message(message.chat.id,'Виберіть кому написати повідомлення', reply_markup=markup)
    	else:
    		bot.send_message(message.chat.id, message.from_user.id)
    elif message.text.lower() == 'подивитися нові повідомлення':
        bot.send_message(message.chat.id, 'Прощай')
    elif message.text.lower() == '':
    	pass
        # bot.send_sticker(message.chat.id, 'CAADAgADZgkAAnlc4gmfCor5YbYYRAI')


bot.polling()

# bot.api.get_inbox_v2()
# data = bot.last_json["inbox"]["threads"]
# for item in data:
# 	user_id = str(item["inviter"]["pk"])
# 	bot.send_message(response, user_id)
