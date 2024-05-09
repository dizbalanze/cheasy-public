import my_config
import my_db
import my_open_ai
import my_robokassa
import my_query
import my_robokassa_db
import my_handle
import telebot
from telebot import types
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Bot, BotCommand, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, ConversationHandler

bot_token = my_config.bot_token
tg_bot = telebot.TeleBot(bot_token)


def is_user_subscribed(chat_id, user_id):
    try: return tg_bot.get_chat_member(chat_id, user_id).status in ['member', 'administrator', 'creator']
    except telebot.apihelper.ApiException: return False


def handle_message(update, context):
    user_message = update.message.text
    user_id = update.message.from_user.id
    
    if my_db.get_user_message_limit(user_id) == 0: my_db.set_user_message_limit(user_id, 25)

    if context.user_data.get('awaiting_review', False):
        my_db.save_user_review(user_id, user_message)
        keyboard = [[InlineKeyboardButton('Продолжить диалог с GPT', callback_data = 'gogpt')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(text = 'Спасибо за ваш отзыв! ❤️', reply_markup = reply_markup)
        context.user_data['awaiting_review'] = False

    elif not is_user_subscribed(my_config.channel_id, user_id):
        start = f'К сожалению, я не вижу, что вы подписались на Ивана. Возможно что-то пошло не так, проверьте еще раз подписку на канал {my_config.chat_link} и нажмите кнопку "Подписался✅", после чего вы сможете задавать мне любые вопросы)'
        keyboard = [[InlineKeyboardButton('Подписался✅', callback_data = 'i_reg')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(start, reply_markup = reply_markup)

    elif my_db.get_user_message_limit(user_id) <= my_db.count_all_messages(user_id):
        start = '''Ууупс, вижу, что у вас закончились запросы.\n\n💰 Если хотите ещё запросов, то вы можете их получить посредством <b>приглашения друга</b> или просто <b>пополнить баланс.</b>'''
        keyboard = [[InlineKeyboardButton('Пополнить баланс', callback_data = 'payment')],
                    [InlineKeyboardButton('Пригласить друга', callback_data = 'friend')], ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(start, reply_markup = reply_markup, parse_mode='HTML')

    elif len(user_message) > 4000:
        update.message.reply_text('ERROR: максимальная длина сообщения превышена')

    else: process_user_message(user_id, user_message, update, context)


def process_user_message(user_id, user_message, update, context):
    my_db.add_message_to_db(user_id, user_message, "user")
    mess = my_db.get_user_messages(user_id)
    total_length = 0

    i = len(mess) - 1
    while total_length < 6000 and i > 0:
        total_length += len(mess[i]['content'])
        i -= 1

    mess = mess[i:]

    temp_message = update.message.reply_text('Генерация ответа может занять до 3-х минут...')
    temp_message_id = temp_message.message_id

    response = my_open_ai.create_completion(mess)
    my_db.add_message_to_db(user_id, response, "assistant")

    update.message.reply_text(response)
    context.bot.delete_message(chat_id=user_id, message_id=temp_message_id)


this_commands = [('start', my_handle.handle_start_command),
                 ('gpt', my_handle.handle_gogpt_command),
                 ('balance', my_handle.handle_balance_command),
                 ('referal', my_handle.handle_referal_command),
                 ('rating', my_handle.handle_rating_command),
                 ('offer', my_handle.handle_offer_command),
                 ('present', my_handle.handle_present_command),]

menu_commands = [('gpt', 'Диалог с Нейросетью'),
                 ('balance', 'Посмотреть и пополнить баланс'),
                 ('referal', 'Реферальная система'),
                 ('rating', 'Оставить отзыв')]

this_buttons = [(my_query.handle_rating_response, '^rate_[1-5]$'),
                (my_query.handle_buy, '^buy_\\d+$'),
                (my_query.handle_check, '^check_\\d+$'),
                (my_query.handle_payment, 'payment'),
                (my_query.handle_friend,'friend'),
                (my_query.handle_mykey, 'mykey'),
                (my_query.handle_gogpt, 'gogpt'),
                (my_query.handle_dialog, '^page_[2-3]$'),]


def main():
    updater = Updater(token=bot_token, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(ConversationHandler(entry_points=[CallbackQueryHandler(my_query.handle_refkey, pattern='refkey')],
        states={0: [MessageHandler(Filters.text & ~Filters.command, my_query.handle_invitation_code)],},
        fallbacks=[]))

    for command, handler in this_commands:
        dp.add_handler(CommandHandler(command, handler))

    for function, pattern in this_buttons:
        dp.add_handler(CallbackQueryHandler(function, pattern = pattern))

    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    my_db.create_db()
    my_robokassa_db.create_database()
    Bot(bot_token).set_my_commands([BotCommand(command, description) for command, description in menu_commands])
    main()