from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep
from selenium.webdriver.common.action_chains import ActionChains


# Выбор опции метро в выпадающем меню
def set_actions(driver,element):
    actions = ActionChains(driver)
    actions.move_to_element(element)
    actions.move_by_offset(0,40)
    actions.click()
    actions.perform()


def subway_route(from_, to_):
    driver = webdriver.Chrome()

    maps = 'https://yandex.ru/maps/213/moscow/?ll=37.622504%2C55.753211&z=10'

    driver.get(maps)
    driver.maximize_window()
    directions = driver.find_element_by_xpath('/html/body/div[1]/div[2]/div[2]/div/div/div/form/div[5]/div/div')
    directions.click()

    sleep(0.5)

    fields = driver.find_elements_by_class_name('input__control')
    where_from = fields[1]
    where_from.send_keys(from_)
    set_actions(driver,where_from)


    sleep(1)

    where_to = fields[2]
    where_to.send_keys(to_)
    set_actions(driver,where_to)


    options = driver.find_element_by_class_name('route-travel-modes-view__comparison-button')
    options.click()
    sleep(2)
    soup = BeautifulSoup(driver.page_source,'lxml')

    #Поиск тега, содержащего данные о времени в пути на метро
    subway = soup.find_all('div', class_="route-snippet-view _comparison _type_masstransit")[0].find('div', class_ = 'comparison-route-snippet-view__route-time-text')
    subway_time = subway.text

    try:
        all = subway_time.split('ч')
        hours = all[0].split('\xa0')[0]
        minutes = all[1][1:].split('\xa0')[0]
        result = int(hours)*60 + int(minutes)
    except:
        result = int(subway_time.split('\xa0')[0])

    driver.quit()
    return(result)

print(subway_route('щелковская','курская'))



# import telebot
# token = ''
# bot = telebot.TeleBot(token)
#
# @bot.message_handler(commands=['start'])
#
# def greetings(message):
#     bot.send_message(message.chat.id, 'Привет, я бот Дубков. Я помогу тебе добраться до дома')
#
#
# bot.polling()

