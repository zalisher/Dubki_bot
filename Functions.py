from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import schedule
import time
import pandas as pd

# Выбор опции метро в выпадающем меню
def set_actions(driver,element):
    actions = ActionChains(driver)
    actions.move_to_element(element)
    actions.move_by_offset(0,40)
    actions.click()
    actions.perform()

# Расчет времени движения через метро
def subway_route(from_, to_):
    driver = webdriver.Chrome()

    maps = 'https://yandex.ru/maps/213/moscow/?ll=37.622504%2C55.753211&z=10'

    driver.get(maps)
    driver.maximize_window()
    directions = driver.find_element_by_xpath('/html/body/div[1]/div[2]/div[2]/div/div/div/form/div[5]/div/div')
    directions.click()

    time.sleep(0.5)

    fields = driver.find_elements_by_class_name('input__control')
    where_from = fields[1]
    where_from.send_keys(from_)
    set_actions(driver,where_from)


    time.sleep(1)

    where_to = fields[2]
    where_to.send_keys(to_)
    set_actions(driver,where_to)


    options = driver.find_element_by_class_name('route-travel-modes-view__comparison-button')
    options.click()
    time.sleep(2)
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

    if to_=='Фили':
        result += 7
    elif to_=='Кунцевская':
        result += 10
    else:
        result += 7

    driver.quit()
    return(result)


# Сбор актувльного расписания по 3 станциям на следующий день
def daily_schedule():
    #   1. Беговая
    #   2. Кунцево
    #   3. Фили

    url_list = {'Begovaya':'https://www.tutu.ru/rasp.php?st1=201&st2=1701&date=tomorrow&print=yes',
                'Kuntsevo':'https://www.tutu.ru/rasp.php?st1=501&st2=1701&date=tomorrow&print=yes',
                'Fili':'https://www.tutu.ru/rasp.php?st1=401&st2=1701&date=tomorrow&print=yes'}

    for name, url in url_list.items():
        driver = webdriver.Chrome()

        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'lxml')
        res = soup.find('table', class_='schedule_table_classic').find('tbody')
        driver.quit()

        trs = res.find_all('tr')
        data = {'Abfahrt': [], 'Odi_min': [], 'Abfahrt_min': [], 'Odi': []}

        for tr in trs:
            time = tr.find_all('a')
            a1 = str(time[0].text)
            data['Abfahrt'].append(a1)
            min_only1 = int(a1.split(':')[0]) * 60 + int(a1.split(':')[1])
            data['Abfahrt_min'].append(min_only1)

            a2 = str(time[1].text)
            data['Odi'].append(str(a2))
            min_only2 = int(a2.split(':')[0]) * 60 + int(a2.split(':')[1])
            data['Odi_min'].append(min_only2)

        final_table_tomorrow = pd.DataFrame(data)

        final_table_tomorrow = final_table_tomorrow.sort_values(by='Abfahrt_min')
        final_table_tomorrow.to_csv('schedule_tomorrow_'+name+'.csv')
        print('done')


# schedule.every(10).seconds.do(daily_schedule)

def schedule_init():
    schedule.every().day.at('03:00').do(daily_schedule)

    while True:
        schedule.run_pending()
        time.sleep(1)