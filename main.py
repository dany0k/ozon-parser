import re

from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as bs4, Tag
import json
import pandas as pd
import numpy as np

captured_data = []
# search = '3070'
search = 'масляный+фильтр+гранта'
# начальная строка
url = f"https://www.ozon.ru/category/maslyanye-filtry-8707/?category_was_predicted=true&deny_category_prediction=true&from_global=true&text={search}"

cookies = list()

firefox_options = FirefoxOptions()
firefox_options.add_argument("-headless")
driver = webdriver.Firefox(options=firefox_options)

driver.get(url)


def page_open(url):
    driver.delete_all_cookies()
    for cookie in cookies:
        # driver.add_cookie(cookies[8])
        driver.add_cookie(cookies[0])
        driver.add_cookie(cookies[1])
        driver.add_cookie(cookies[2])
        driver.add_cookie(cookies[4])
        # получаем страницу
    driver.get(url)

    try:
        # ждем пока не появится на странице тэг с id ozonTagManagerApp
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ozonTagManagerApp"))
        )
    finally:
        # возвращаем текст страницы
        return driver.page_source


def images_dict(good_id: int, mask: str, soup) -> dict:
    images_dictionary = []
    try:
        # ищем div у которого в атрибуте data-state есть название имени файла
        data = soup.select_one(f'div[data-state*="{mask}"]')['data-state']
        # данные представлены в json формате, так что используем это и преобразуем в словарь
        json_data = json.loads(data)
        # зная структуру json данных, находим в словаре нужные нам данные
        for link in json_data['items'][good_id]['tileImage']['items']:
            images_dictionary.append(link['image']['link'])
        return images_dictionary
    except:
        return []


def options_dictionary(options_list: list) -> dict:
    options_dict = {}
    for option in options_list:
        options_dict[option.split(':')[0].strip()] = option.split(':')[1].strip()
    return options_dict


def func_parse(items):
    idx = 0
    for sibling in items:
        if isinstance(sibling, Tag) and sibling.text:
            # создаем словарь, куда будем помещать все полученные данные для товара
            item = {}
            bonuses = False
            # если есть бонусы за товар, получаем их
            if t := sibling.div.next_sibling.next_sibling.select_one('div span > span b'):
                print(t.text)
                item['bonuses'] = t.text
                bonuses = True
            # получаем название товара
            # print(item_name := sibling.div.next_sibling.next_sibling.div.a.span.span.text)
            # item['name'] = item_name

            # получаем основную картинку предпросмотра
            img = sibling.div.a.div.div.img['src']
            item['preimage'] = img

            print(item_images := images_dict(idx, img.split('/')[-1], soup))
            item['images'] = item_images

            # если бонусы были, то смещаемся на один таг span
            n_child = 3 if bonuses else 2

            # вы таскиваем все options для товара
            if options := sibling.div.next_sibling.next_sibling.select_one(f'div > span:nth-child({n_child}) span'):
                options_str = str(options)
                # вырезаем ненужные тэги
                cleaned_str = re.sub(r'<?.span>|<font color="#......">|</font>', '', options_str)
                print(item_options := options_dictionary(cleaned_str.split('<br/>')))
                item['options'] = item_options
            idx += 1

            # в месте цены, html фрмируется по разному - обходим эти два варианта
            if price := sibling.div.next_sibling.next_sibling.next_sibling.next_sibling.div.div:
                print((price_text := price.text[:-1].replace(' ', '')))
                # цена идет в кодировке, которая нам не подходит, возвращаем к человеческому виду
                item['price'] = int(price_text.encode('ascii', 'ignore'))
                # item['price'] = price_text
            elif price := sibling.div.next_sibling.next_sibling.next_sibling.next_sibling.div.span.span:
                print((price_text := price.text[:-1].replace(' ', '')))
                item['price'] = int(price_text.encode('ascii', 'ignore'))
                # item['price'] = price_text

            # добавляем наш товар в список товаров
            captured_data.append(item)


def options_parser(row):
    for option in options_set:
        row[option] = (row['options'].get(option))
    return row


for page in range(1, 2):
    # добавляем нужную страницу к url и отправляем в функцию pageOpen на скачку
    source_text = page_open(f'{url}&page={page}')
    # удаляем из текста всякие комментарии, чтобы не болтались мертвым грузом. Но это не обязательно
    result = re.sub(r'<!.*?->', '', source_text)
    # создаем обьект bs4, на основе скаченного html
    soup = bs4(result, 'html.parser')
    # Находим нужный нам html обьект по тагу и его id - там хранятся данные о товарах
    items_body = soup.find('div', id='paginatorContent')
    # переходим на нужные теги
    items = items_body.div.div
    # парсим данные
    func_parse(items=items)

for sibling in items:
    if sibling.text:
        print(sibling)

for sibling in items:
    if isinstance(sibling, Tag) and sibling.text:
        print((sibling))

for sibling in items:
    if isinstance(sibling, Tag):
        print(sibling.div.next_sibling.next_sibling.select_one('div span > span b'))

for sibling in items:
    if isinstance(sibling, Tag):
        print(item_name := sibling.div.next_sibling.next_sibling.div.a.text)

for sibling in items:
    if isinstance(sibling, Tag):
        print(img := sibling.div.a.div.div.img['src'])
        print(img_list := img.split('/')[-1])

print(data := soup.select_one(f'div[data-state*="{img_list}"]')['data-state'])
json_data = json.loads(data)
json_data
json_data['items'][0]['tileImage']['items']

for sibling in items:
    if isinstance(sibling, Tag):
        print(a := sibling.div.next_sibling.next_sibling.select_one('div > span:nth-child(2) span'))
        t_a = re.sub(r'<?.span>|<font color="#......">|</font>', '', str(a))
        print(t_a)
        print(t_a.split('<br/>'))
        print(item_options := options_dictionary(t_a.split('<br/>')))

df = pd.DataFrame(captured_data)
options_set = set()
for i in captured_data:
    options_set = set(i['options'].keys()) | options_set

#  создаем новые колонки согласно опциям
for col in options_set:
    df[col] = np.nan

df = df.apply(options_parser, axis = 1)
df = df.drop(columns=['options'])
df.head(3)
df.to_excel('ozon_parse.xlsx')

driver.quit()
