from typing import List
from telegram import Bot
from telegram.ext import Updater, CommandHandler
import rpyc

pt: int = 18861


class TelegramDispatcher:

    def _rpyc_getattr(self, name):
        if name.startswith("_"):
            # disallow special and private attributes
            raise AttributeError("cannot accept private/special names")
        # allow all other attributes
        return getattr(self, name)

    def __init__(self, tele_bot_token):
        self.subscribers: List[str] = []
        self.tele_bot_token = tele_bot_token

    def add_subscribers(self, subs_id: str):
        self.subscribers.append(subs_id)

    def pop_subscribers(self, subs_id: str):
        self.subscribers.remove(subs_id)

    def get_subscribers(self):
        return self.subscribers

    def send_telegram_message(self, send_to_id: str, message: str):
        bot = Bot(token=self.tele_bot_token)
        print(message)
        bot.send_message(chat_id=send_to_id, text=message)

    # sending message to all subscribe user
    def send_all_subs(self, message: str):
        # send message to each subscribers provided that they are subscribing
        for sub_id in self.subscribers:
            self.send_telegram_message(sub_id, message)


def connect_recording_service(port):
    conn = rpyc.connect('localhost', port=port)
    return conn.root


# create callback function
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")
    conn_root = connect_recording_service(port=pt)
    sub_id = update.effective_chat.id
    if sub_id not in conn_root.telegram_dispatch.get_subscribers():
        conn_root.telegram_dispatch.add_subscribers(sub_id)
        context.bot.send_message(chat_id=sub_id, text='You are subscribing now')
    else:
        context.bot.send_message(chat_id=sub_id, text='You are already subscribing')


def subscribe(update, context):
    conn_root = connect_recording_service(port=pt)
    sub_id = update.effective_chat.id
    if sub_id not in conn_root.telegram_dispatch.get_subscribers():
        conn_root.telegram_dispatch.add_subscribers(sub_id)
        context.bot.send_message(chat_id=sub_id, text='You are subscribing now')
    else:
        context.bot.send_message(chat_id=sub_id, text='You are already subscribing')


def unsubscribe(update, context):
    conn_root = connect_recording_service(port=pt)
    sub_id = update.effective_chat.id
    if sub_id in conn_root.telegram_dispatch.get_subscribers():
        conn_root.telegram_dispatch.pop_subscribers(sub_id)
        context.bot.send_message(chat_id=sub_id, text='You are not subscribing')
    else:
        context.bot.send_message(chat_id=sub_id, text='You are already unsubscribing')


def start_telegram_service(tele_bot_token, port):
    global pt
    pt = port
    updater = Updater(token=tele_bot_token)

    # dispatcher will automatically be created once updater is set up
    dispatcher = updater.dispatcher

    # create handler
    handlers = [CommandHandler('start', start),
                CommandHandler('sub', subscribe),
                CommandHandler('unsub', unsubscribe)]
    list(map(dispatcher.add_handler, handlers))

    # start the bot
    updater.start_polling(poll_interval=5)
