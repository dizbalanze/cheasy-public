import my_config
import my_db

import telebot
from telebot import types
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Bot, ParseMode
from telegram.ext import ConversationHandler

bot_token = my_config.bot_token
tg_bot = telebot.TeleBot(bot_token)


def handle_start_command(update, context):
    user_id = update.effective_user.id
    if not my_db.check_user_exists(user_id):
        my_db.set_user_message_limit(user_id, 25)
        my_db.set_user_registration_status(user_id, False)

    start = 'Привет!\n\nЯ - аналог ChatGPT, меня создали для удобства российских граждан в использовании нейросетей. Мои создатели увидели, как проблемно иногда бывает людям заходить в ChatGPT через VPN, а также оплачивать сервис с иностранных карт. Мое существование полностью решает эту проблему)\n\nМеня создали недавно, и мой создатель хочет понять реально ли вам - людям, я нужна. Поэтому я изо всех сил постараюсь быть вам полезной и решать ваши задачи максимально эффективно.\n\nДля того чтобы понять нужна ли я вам, мой создатель первым 100 людям дает возможность пообщаться со мной абсолютно бесплатно. У вас будут несгораемые 25 запросов, которые вы сможете использовать в любой момент.'
    keyboard = [[InlineKeyboardButton('Супер, когда начнем?', callback_data = 'page_2')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(start, reply_markup=reply_markup)


def handle_balance_command(update, context):
    user_id = update.message.from_user.id
    m_limit = my_db.get_user_message_limit(user_id)
    messages_sent = my_db.count_all_messages(user_id)
    if m_limit == 0:
        my_db.set_user_message_limit(user_id, 25)
        m_limit = 25
    text = f'☑️ Вы можете еще отправить: *{m_limit - messages_sent} запросов*.\n\n☑️ Всего вы потратили: *{messages_sent} запросов*.\n\n💰 Если хотите ещё запросов, то вы можете их получить посредством *приглашения друга* или просто *пополнить баланс*.'
    keyboard = [[InlineKeyboardButton('Пополнить баланс', callback_data = 'payment')],
                [InlineKeyboardButton('Пригласить друга', callback_data = 'friend')],]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)


def handle_referal_command(update, context):
    user_id = update.message.from_user.id
    m_limit = my_db.get_user_message_limit(user_id)
    if m_limit == 0:
        my_db.set_user_message_limit(user_id, 25)

    text = 'Добро пожаловать в нашу реферальную систему!\n\nТеперь вы можете делиться нашим сервисом со своими друзьями и получать выгоду. За каждого приглашенного вами друга вы будете получать 10 запросов, с помощью которых вы сможете общаться с нейросетью абсолютно бесплатно 💸\n\n🤔 <b>Как это работает?</b>\n\n👉 <b>Вы</b> рекомендуете своему другу нас и предоставляете ему свой реферальный ключ. \n👈 <b>Мы</b> начисляем и вам и вашему другу по 🔟 <b>бесплатных запросов</b> каждому.\n\n<i>WIN - WIN</i> 🤝'
    keyboard = [[InlineKeyboardButton('Ввести ключ друга', callback_data = 'refkey')],
                [InlineKeyboardButton('Узнать свой ключ', callback_data = 'mykey')], ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(text, parse_mode = 'HTML', reply_markup = reply_markup)


def handle_rating_command(update, context):
    user_id = update.message.from_user.id
    start = '''📌 Надеюсь у вас уже получилось попробывать весь мой функционал  🤖\n\n📌 Очень вас прошу оставить обратную связь и выбрать честную оценку моей работы 🙂\n\n📌 В этом разделе вы в любой момент можете оставить свою оценку, и написать моим создателям)'''
    keyboard = [[InlineKeyboardButton('1', callback_data = 'rate_1'),
                 InlineKeyboardButton('2', callback_data = 'rate_2'),
                 InlineKeyboardButton('3', callback_data = 'rate_3'),
                 InlineKeyboardButton('4', callback_data = 'rate_4'),
                 InlineKeyboardButton('5', callback_data = 'rate_5')]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(start, reply_markup=reply_markup)


def handle_gogpt_command(update, context):
    user_id = update.effective_user.id
    if not my_db.check_user_exists(user_id):
        my_db.set_user_message_limit(user_id, 25)
        my_db.set_user_registration_status(user_id, False)

    start = '🚀 Напишите свой запрос, и я максимально подробно на него отвечу 🚀'
    update.message.reply_text(start)


def handle_offer_command(update, context):
    user_id = update.effective_user.id
    if user_id in my_config.admins:
        bot = Bot(bot_token)
        user_message = update.message.text
        text_after_command = user_message.replace('/offer ', '', 1).replace("%id%", str(user_id))

        ids = my_db.get_all_user_ids()
        for id in ids:
            try: bot.send_message(chat_id=id, text=text_after_command)
            except Exception: print(f"Ошибка: {Exception}")


def handle_present_command(update, context):
    user_id = update.effective_user.id
    i = 1
    for s in update.message.text.split(' '):
        print(f'{i}: {s}')
        i += 1
    if user_id in my_config.admins:
        try:
            arr = update.message.text.split(' ')
            my_db.set_user_message_limit(arr[1], my_db.get_user_message_limit(int(arr[1])) + int(arr[2]))
        except: return
