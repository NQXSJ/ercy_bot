import openai
import telegram

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

import os
import logging
import redis
openai.api_key = os.environ['API']
global redis1


def main():
    updater = Updater(token=(os.environ['ACCESS_TOKEN']))
    dispatcher = updater.dispatcher

    global redis1

    redis1 = redis.StrictRedis(host=(os.environ['HOST']),
       port=6380, db=0, password=(os.environ['PASSWORD']), ssl=True)
    result = redis1.ping()
    print("Ping returned : " + str(result))

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    dispatcher.add_handler(echo_handler)

    dispatcher.add_handler(CommandHandler("count", count))

    updater.start_polling()
    updater.idle()


def echo(update, context):
    temp = context.bot.send_message(chat_id=update.effective_chat.id, text="🤔Please wait while we organize the language.")
    context.bot.sendChatAction(update.effective_chat.id, 'typing')
    response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": update.message.text}
            ],
            max_tokens=1024,
        )
    global redis1
    redis1.incr('question')
    logging.info(redis1.get('question'))
    logging.info("Question: " + str(update.message.text))
    message = response["choices"][0]["message"]['content']
    logging.info("AI response: " + str(message))
    context.bot.editMessageText(chat_id=update.message.chat_id,
                                message_id=temp.message_id, 
                                text=message)

def count(update: Update, context: CallbackContext) -> None:
    try:
        global redis1
        update.message.reply_text(
            'Our AI bot has already responded to ' + redis1.get('question').decode('UTF-8') + ' questions')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /count')


if __name__ == '__main__':
    main()
