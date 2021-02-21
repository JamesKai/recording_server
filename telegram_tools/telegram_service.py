from telegram.ext import Updater, CommandHandler
import rpyc

pt: int = 18861


def connect_recording_service(port):
    conn = rpyc.connect('localhost', port=port)
    return conn.root


# create callback function
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")


def subscribe(update, context):
    conn_root = connect_recording_service(port=pt)
    sub_id = update.effective_chat.id
    if sub_id not in conn_root.get_subscribers():
        conn_root.add_subscribers(sub_id)
        context.bot.send_message(chat_id=sub_id, text='You are subscribing now')
    else:
        context.bot.send_message(chat_id=sub_id, text='You are already subscribing')


def unsubscribe(update, context):
    conn_root = connect_recording_service(port=pt)
    sub_id = update.effective_chat.id
    if sub_id in conn_root.get_subscribers():
        conn_root.pop_subscribers(sub_id)
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
