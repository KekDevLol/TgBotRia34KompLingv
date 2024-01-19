import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import sqlite3
from telegram.ext import CallbackContext
from db_utils import get_db_connection

def parse_and_insert_news(context: CallbackContext):
    # Подключение к базе данных SQLite
    conn = get_db_connection()
    cursor = conn.cursor()

    url_base = 'https://riac34.ru/news/'
    limit_news_per_hour = 12
    current_news = 0

    while current_news < limit_news_per_hour:
        response = requests.get(url_base)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            news_blocks = soup.find_all('div', class_='new-block')

            for news_block in news_blocks:
                title = news_block.find('a', class_='caption').text.strip()
                date = news_block.find('span', class_='date').text.strip()
                link_relative = news_block.find('a', class_='caption')['href']

                # Объединение относительной ссылки с базовым URL
                link_absolute = urljoin(url_base, link_relative)

                # Создание нового курсора для каждой итерации цикла
                cursor.execute('SELECT id FROM news WHERE date=? AND link=?', (date, link_absolute))
                existing_news = cursor.fetchone()

                if existing_news:
                    print(f'Новость уже существует, пропуск: {title} - {date} - {link_absolute}')
                    current_news += 1
                    continue

                # Получение текста новости с полной страницы
                full_text_response = requests.get(link_absolute)
                if full_text_response.status_code == 200:
                    full_text_soup = BeautifulSoup(full_text_response.text, 'html.parser')
                    full_text = full_text_soup.find('div', class_='full-text').text.strip()
                else:
                    full_text = ''

                # Вставка данных в базу данных
                cursor.execute('''
                    INSERT INTO news (title, date, link, full_text) VALUES (?, ?, ?, ?)
                ''', (title, date, link_absolute, full_text))
                conn.commit()

                current_news += 1
                print(f'Пропарсено новостей: {current_news}/{limit_news_per_hour}')

                if current_news >= limit_news_per_hour:
                    break

            # Пагинация
            pagination = soup.find('div', class_='pagination')
            next_page = pagination.find('a', class_='next')['href']
            url_base = urljoin(url_base, next_page)

        else:
            print(f'Ошибка при запросе: {response.status_code}')
            break

    print('Парсинг завершен. Данные сохранены в базе данных.')

    # Закрытие курсора и соединения с базой данных
    cursor.close()
    conn.close()
