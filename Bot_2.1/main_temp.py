import json
import requests
from datetime import datetime
import telebot
from telebot import types


TOKEN = '7848995107:AAEXT_s5PPlBZP-9Kv88PA1R5qcYFp92OJk'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    item1 = types.KeyboardButton('⚽️ Перезапуск Алгоритма!')
    item2 = types.KeyboardButton('⚙️ Запустить проверку Бота!')
    item3 = types.KeyboardButton('✉️ Написать в техподдержку!')

    markup.add(item1)
    markup.row(item2,item3)

    bot.send_message(message.chat.id, 'Привет {0.first_name}! Жди сигнал - идет анализ матчей! 😉'.format(message.from_user), reply_markup=markup)

@bot.message_handler(func=lambda msg: msg.text in ["⚽️ Перезапуск Алгоритма!", "⚙️ Запустить проверку Бота!", "✉️ Написать в техподдержку!"])
def handle_menu_buttons(message):
    
    if message.text == '⚽️ Перезапуск Алгоритма!':
         text = (
             #####################################





             '⏳ Бот анализирует матчи 3!'
             





             
             #####################################
             )

         bot.send_message(message.chat.id, text)

         txt = ('⚠️ Ошибка в Алгоритме! Обратитесь в техподдержку!')
         # Выводим сообщение в телеграм
         bot.send_message(message.chat.id, txt)




    elif message.text == '⚙️ Запустить проверку Бота!':
        bot.send_message(message.chat.id, '🟢 Всё в порядке! Бот работает Прекрасно! 👌')   

    elif message.text == '✉️ Написать в техподдержку!':
        bot.send_message(message.chat.id, 'Обращайся по любым вопросам! Контакты в нашем канале: @betbotlab')   

#####################################



bot.polling(none_stop=True)
if __name__ == '__main__':
    analyze_matches()







    
#                        txt = f'''
# 🏆 {liga}

# ⚽️ {k1} ⚔️ {k2}

# --------------------------------------------
# ⏰ Время матча: {m_date}
# --------------------------------------------
# Начальные коэффициенты:
# П1 - {tkf1}  П2 - {tkf2}
# --------------------------------------------

# 🔥 Прогноз: Тотал Больше 3.5 
# '''     