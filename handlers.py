from datetime import datetime, timedelta
from telegram import Update, ParseMode, utils
from telegram.ext import CallbackContext
import sqlite3
from db_utils import get_db_connection
import telegram.utils.helpers as helpers
# Подключение к базе данных SQLite
conn = sqlite3.connect('news_database.db')
cursor = conn.cursor()


def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    start_time = datetime.now()

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Создание нового курсора для каждой операции
        cursor.execute('INSERT OR IGNORE INTO users (chat_id, start_time) VALUES (?, ?)', (user_id, start_time))
        conn.commit()
        update.message.reply_text('Добро пожаловать! Вы подписались на новости.')

    except Exception as e:
        print(f'Ошибка при выполнении команды /start: {e}')

    finally:
        # Закрытие курсора и соединения с базой данных
        cursor.close()
        conn.close()

    # Сохраняем пользовательские данные в контексте для использования в других функциях
    context.user_data['user_id'] = user_id
    context.user_data['start_time'] = start_time


def send_news_to_users(context: CallbackContext):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Получаем чат-иды подписчиков
        cursor.execute('SELECT chat_id FROM users')
        user_data_list = cursor.fetchall()

        # Получаем 12 новостей с самым большим id
        cursor.execute('SELECT * FROM news ORDER BY id DESC LIMIT 12')
        news_to_send = cursor.fetchall()

        # Фильтруем новости, оставляем только те, у которых sent = 0
        news_to_send = [news for news in news_to_send if news[5] == 0]

        for user_data in user_data_list:
            user_id = user_data[0]

            for news in news_to_send:
                # Ограничиваем вывод сообщения 200 символами
                truncated_message = f"📰 *{news[1]}*\n_{news[2]}_\n[Подробнее]({news[3]})\n{news[4]}"[:1000]

                # Отправляем каждую новость в чат подписчика
                context.bot.send_message(user_id, text=truncated_message, parse_mode=ParseMode.MARKDOWN,
                                         disable_web_page_preview=True)

                # Помечаем новость как отправленную
                cursor.execute('UPDATE news SET sent = 1 WHERE id = ?', (news[0],))
                conn.commit()

    except Exception as e:
        print(f'Ошибка при отправке новостей: {e}')

    finally:
        conn.close()