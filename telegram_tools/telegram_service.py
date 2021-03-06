from typing import List

import rpyc
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler

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
        bot.send_message(chat_id=send_to_id, text=message)

    # sending message to all subscribe user
    def send_all_subs(self, message: str):
        # send message to each subscribers provided that they are subscribing
        for sub_id in self.subscribers:
            self.send_telegram_message(sub_id, message)


def connect_recording_service(port):
    recording_service = rpyc.connect('localhost', port=port)
    return recording_service.root


def start(update: Update, context: CallbackContext):
    chat_id = update.message.from_user.id
    context.bot.send_message(
        chat_id=chat_id,
        text='Choose the option in main menu:',
        reply_markup=main_menu_keyboard(),
    )


def main_menu(update: Update, _context: CallbackContext):
    update.callback_query.message.edit_text('Choose the option in main menu:',
                                            reply_markup=main_menu_keyboard())


def sub_page(update: Update, context: CallbackContext):
    recording_service = connect_recording_service(port=pt)
    sub_id = update.effective_chat.id
    if sub_id not in recording_service.telegram_dispatch.get_subscribers():
        recording_service.telegram_dispatch.add_subscribers(sub_id)
        message = "You are subscribed"
    else:
        message = "You are already subscribed"
    update.callback_query.message.edit_text(message,
                                            reply_markup=sub_page_keyboard())


def unsub_page(update: Update, context: CallbackContext):
    recording_service = connect_recording_service(port=pt)
    sub_id = update.effective_chat.id
    if sub_id in recording_service.telegram_dispatch.get_subscribers():
        recording_service.telegram_dispatch.pop_subscribers(sub_id)
        message = "You are not subscribed"
    else:
        message = 'You are already unsubscribed'
    update.callback_query.message.edit_text(message,
                                            reply_markup=unsub_page_keyboard())


def finish_time_page(update: Update, context: CallbackContext):
    recording_service = connect_recording_service(port=pt)
    message = recording_service.calculator.estimate_finish_time()
    update.callback_query.message.edit_text(message,
                                            reply_markup=finish_time_page_keyboard())


def main_menu_keyboard():
    keyboard = [[InlineKeyboardButton('Subscribe', callback_data='sub_page'),
                 InlineKeyboardButton('Unsubscribe', callback_data='unsub_page')],
                [InlineKeyboardButton('Predict Finish Time', callback_data='finish_time_page')]]
    return InlineKeyboardMarkup(keyboard)


def sub_page_keyboard():
    keyboard = [
        [InlineKeyboardButton('Back to Menu', callback_data='main')]]
    return InlineKeyboardMarkup(keyboard)


def unsub_page_keyboard():
    keyboard = [
        [InlineKeyboardButton('Back to Menu', callback_data='main')]]
    return InlineKeyboardMarkup(keyboard)


def finish_time_page_keyboard():
    keyboard = [
        [InlineKeyboardButton('Back to Menu', callback_data='main')]]
    return InlineKeyboardMarkup(keyboard)


def start_telegram_service(tele_bot_token, port):
    global pt
    pt = port
    updater = Updater(token=tele_bot_token)

    # dispatcher will automatically be created once updater is set up
    dispatcher = updater.dispatcher

    # create handler
    handlers = [
        CommandHandler('start', start),
        CallbackQueryHandler(main_menu, pattern='main'),
        CallbackQueryHandler(sub_page, pattern='sub_page'),
        CallbackQueryHandler(unsub_page, pattern='unsub_page'),
        CallbackQueryHandler(finish_time_page, pattern='finish_time_page')
    ]
    list(map(dispatcher.add_handler, handlers))

    # start the bot
    updater.start_polling(poll_interval=3)
