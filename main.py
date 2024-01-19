from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from handlers import start, send_news_to_users
from parser import parse_and_insert_news

def main():
    # Замените 'YOUR_BOT_TOKEN' на фактический токен вашего бота
    updater = Updater(token='6923984188:AAHmGLDeJGQCli4E0uXaHbZElLJ-8cLAzp0', use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, lambda update, context: None))

    updater.job_queue.run_repeating(send_news_to_users, interval=60, first=0, context={'user_data': {}})
    updater.job_queue.run_repeating(parse_and_insert_news, interval=60, first=0)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()