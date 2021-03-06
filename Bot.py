import datetime
import pandas as pd
import Functions
import telebot
import threading
import time


keyboard2 = telebot.types.InlineKeyboardMarkup();  # наша клавиатура
key_one = telebot.types.InlineKeyboardButton(text='Беговая', callback_data='begov')
keyboard2.add(key_one); #добавляем кнопку в клавиатуру
key_two = telebot.types.InlineKeyboardButton(text='Фили', callback_data='fili');
keyboard2.add(key_two);
key_three = telebot.types.InlineKeyboardButton(text='Кунцевская', callback_data='kunts');
keyboard2.add(key_three);

token = ""
bot = telebot.TeleBot(token)


def route_calc(message,where_from,where_to,alias):
    # Перемещение в метро
    on_the_go = Functions.subway_route(where_from,where_to)

    # Получаем информацию о текущем времени
    # Попробую поставить в хендлеры бота. Пока не знаю, как он будет работать для множества людей
    # Можно поробовать создавать словарь с ключем - номером чата собеседника
    now = datetime.datetime.today()
    now_str = str(now)
    now_calc = now_str[11:16].split(':')

    # Время, к которому мы прибудем на станцию электричек, on_the_go учитывает время, чтобы добраться
    before_the_train = int(now_calc[0])*60 + int(now_calc[1]) + on_the_go



    # Выбираем подходящую электричку
    schedule = pd.read_csv(r'schedule_tomorrow_'+alias+'.csv')
    if before_the_train > 1438:
        result = schedule[schedule['Abfahrt_min'] == min(schedule['Abfahrt_min'])].loc[:,['Abfahrt','Odi','Odi_min']].values[0]
    else:
        target_time_df = schedule[schedule['Abfahrt_min'] >= before_the_train]
        result = target_time_df.loc[:,['Abfahrt','Odi','Odi_min']].values[0]

    # Время, к которому человек будет у автобуса, добавляю 4 минуты, чтобы дойти
    bus_time = result[2] + 4

    #
    # Добавить выходные
    weekday = now.weekday()
    if weekday == 5 or weekday == 6:
        buses = pd.read_csv('Weekends.csv',index_col=0)
    else:
        buses = pd.read_csv('Weekdays.csv', index_col=0)


    if bus_time <= 40 or bus_time > 1422:
        target_bus = '00:40'
    else:
        bs = buses[buses['minutes'] >= int(result[2])]
        target_bus = str(bs.loc[:, ['Odi-Dub']].values[0][0])[12:16]

    bot.send_message(message.chat.id,'Электричка отправляется в {}.\nТы будешь в Одинцово в {}.\nБлижайший автобус в {}'.format(result[0],result[1],target_bus))




@bot.message_handler(commands=['start'])
def greetings(message):
    bot.send_message(message.chat.id, 'Привет, я бот Дубков. Я помогу тебе добраться до дома. \n Напиши комаду /go, чтобы построить маршрут')

@bot.message_handler(commands=['go'])
def start(message):
    msg = bot.send_message(message.chat.id, 'От какого метро поедешь?')
    bot.register_next_step_handler(msg,start)

def start(message):
    global subway_from
    subway_from = message.text

    bot.send_message(message.chat.id, 'Через какую станцию?', reply_markup=keyboard2)


@bot.message_handler(content_types=['text'])
def go_command(message):
    bot.send_message(message.chat.id, 'Напиши /go, чтобы построить маршрут')


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    chat_data = call.message
    global destination
    if call.data == "begov": #call.data это callback_data, которую мы указали при объявлении кнопки
        destination = 'Беговая'
        # alias нужнен для доступа к нужному csv расписанию
        alias = 'Begovaya'
        bot.send_message(chat_data.chat.id, "Рассчитываю маршрут")
        route_calc(chat_data,subway_from,destination,alias)
    elif call.data == "fili":
        bot.send_message(chat_data.chat.id, "Рассчитываю маршрут")
        destination = 'Фили'
        alias = 'Fili'
        route_calc(chat_data,subway_from,destination,alias)
    elif call.data == 'kunts':
        bot.send_message(chat_data.chat.id, "Рассчитываю маршрут")
        destination = 'Кунцевская'
        alias = 'Kuntsevo'
        route_calc(chat_data,subway_from,destination,alias)



t1 = threading.Thread(target = Functions.schedule_init)
t1.start()
time.sleep(5)
t2 = threading.Thread(target = bot.polling())
t2.start()




