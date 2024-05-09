import my_config
import my_db
import my_robokassa
import my_robokassa_db
import telebot
from telebot import types
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import ConversationHandler

bot_token = my_config.bot_token
tg_bot = telebot.TeleBot(bot_token)


def handle_friend(update, context):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id

    m_limit = my_db.get_user_message_limit(user_id)
    if m_limit == 0:
        my_db.set_user_message_limit(user_id, 25)

    text = 'Добро пожаловать в нашу реферальную систему!\n\nТеперь вы можете делиться нашим сервисом со своими друзьями и получать выгоду. За каждого приглашенного вами друга вы будете получать 10 запросов, с помощью которых вы сможете общаться с нейросетью абсолютно бесплатно 💸\n\n🤔 <b>Как это работает?</b>\n\n👉 <b>Вы</b> рекомендуете своему другу нас и предоставляете ему свой реферальный ключ. \n👈 <b>Мы</b> начисляем и вам и вашему другу по 🔟 <b>бесплатных запросов</b> каждому.\n\n<i>WIN - WIN</i> 🤝'
    keyboard = [[InlineKeyboardButton('Ввести ключ друга', callback_data = 'refkey')],
                [InlineKeyboardButton('Узнать свой ключ', callback_data = 'mykey')],]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.message.reply_text(text, parse_mode='HTML', reply_markup=reply_markup)


def handle_refkey(update, context):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id

    if not my_db.get_user_registration_status(user_id):
        query.message.reply_text(f'Здесь вы можете ввести реферальный ключ, пригласившего вас друга.\n\nПосле этого вы получите 10 бесплатных запросов 🔥\n\nПросто напишите мне ключ и я все сделаю 🙂')
        context.user_data['state'] = 0
        return 0
    else: query.message.reply_text('⚠️Ошибка⚠️\nВы уже ввели реферальный ключ.')


def handle_invitation_code(update, context):
    # GOOD
    user_message = update.message.text
    user_id = update.message.from_user.id

    user_exist = my_db.check_user_exists(user_message)
    reg_status = my_db.get_user_registration_status(user_id)
    not_himself = str(user_message) != str(user_id)
    print(user_exist, reg_status, not_himself)
    if str(user_message) == str(user_id): start = 'Ошибка! Нельзя использовать свой собственный код'
    elif user_exist and not_himself and (reg_status != 100):
        my_db.set_user_message_limit(user_id, (my_db.get_user_message_limit(user_id) + 10))
        my_db.set_user_message_limit(int(user_message), (my_db.get_user_message_limit(int(user_message)) + 10))
        my_db.set_user_registration_status(user_id, 100)
        my_db.set_user_registration_status(int(user_message), 100)

        cam = my_db.count_all_messages(user_id)
        start = f'✅ Все готово.\n\n10 запросов начислены на ваш баланс.\n\nТеперь ваш баланс выглядит так:\n\n☑️ Вы можете еще отправить: {my_db.get_user_message_limit(user_id) - cam} запросов.\n\n☑️ Всего вы потратили: {cam} запросов'
        keyboard = [[InlineKeyboardButton("Продолжить диалог с GPT", callback_data = "gogpt")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(start, reply_markup = reply_markup)
        del context.user_data['state']
        return ConversationHandler.END
    elif reg_status == 100: start = 'Вы уже вводили код активации'
    else: start = f'⚠️ Ошибка ⚠️\n\nРеферальный ключ недействителен. Нажмите на кнопку повторно и попробуйте ввести правильный ключ.'
    update.message.reply_text(start)
    del context.user_data['state']
    return ConversationHandler.END


def handle_mykey(update, context):
    # GOOD
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    bot = Bot(bot_token)
    query.message.reply_text(f'Ваш код: {user_id} \n\nЕсли новый участник введёт ваш код после команды /referal, вы оба получите по 10 бесплатных сообщений. Для вашего удобства, мы подготовили готовое сообщение, вам нужно его лишь скопировать и отправить своему другу) 👇')
    text = f'Привет! Попробуй бесплатную нейросеть прямо в ТГ, без каких либо VPN и иностранных карт. Я уже пользуюсь, мне заходит. Просто введи этот код: <code>{user_id}</code> после команды /referal и ты получишь дополнительные 10 запросов. Переходи по ссылке, реально крутая тема: {my_config.chat_link}'
    keyboard = [[InlineKeyboardButton("Продолжить диалог с GPT", callback_data = "gogpt")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.message.reply_text(text, parse_mode = "HTML", reply_markup = reply_markup)


def is_user_subscribed(chat_id, user_id):
    bot = telebot.TeleBot(bot_token)
    try:
        member = bot.get_chat_member(chat_id, user_id)
        print('User ' + member.status)
        return member.status in ['member', 'administrator', 'creator']
    except telebot.apihelper.ApiException:
        return False


def handle_dialog(update, context):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id

    if query.data == 'page_2':
        start = f'Так как я буду для вас бесплатной нейросетью, у меня есть к вам просьба) Для того чтобы начать пользоваться моим бесплатным  функционалом, вам необходимо подписаться на канал моего создателя. Его зовут Иван, в своем канале он рассказывает "Как?" и "Почему?" мои братья и сестры нейро-сотрудники заменят реальных людей, и как вы сможете внедрить нейросети в свой бизнес уже сейчас, обогнав своих конкурентов на километры.\n\nЧтобы перейти в канал и подписаться, вам необходимо пройти по ссылке {my_config.chat_link}\n\nПосле того, как подпишитесь нажмите кнопку "Подписался✅", после чего вы сможете задавать мне любые вопросы)'
        keyboard = [[InlineKeyboardButton('Подписался✅', callback_data = 'page_3')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.message.reply_text(start, reply_markup=reply_markup)

    elif query.data == 'page_3':
        if is_user_subscribed(my_config.channel_id, user_id):
            start = '📌 Вы можете написать свой запрос в любой момент в строке ввода текста.\n\n🚀 Не стесняйтесь, спрашивайте у меня все что угодно !'
            query.message.reply_text(start)
        else:
            start = f'К сожалению, я не вижу, что вы подписались на Ивана. Возможно что-то пошло не так, проверьте еще раз подписку на канал {my_config.chat_link} и нажмите кнопку "Подписался✅", после чего вы сможете задавать мне любые вопросы)'
            keyboard = [[InlineKeyboardButton('Подписался✅', callback_data = 'page_3')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.message.reply_text(start, reply_markup=reply_markup)


def handle_gogpt(update, context):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id

    if is_user_subscribed(my_config.channel_id, user_id):
        start = '🚀 Напишите свой запрос, и я максимально подробно на него отвечу 🚀'
        query.message.reply_text(start)
    else:
        start = f'К сожалению, я не вижу, что вы подписались на Ивана. Возможно что-то пошло не так, проверьте еще раз подписку на канал {my_config.chat_link} и нажмите кнопку "Подписался✅", после чего вы сможете задавать мне любые вопросы)'
        keyboard = [[InlineKeyboardButton('Подписался✅', callback_data = 'page_3')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.message.reply_text(start, reply_markup = reply_markup)


def handle_buy(update, context):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id

    amount = int(query.data.split("_")[1])
    pay_id = my_robokassa_db.count_payment_ids() + 300
    context.user_data['amount'] = amount
    context.user_data['pay_id'] = pay_id
    my_robokassa_db.add_payment_user(pay_id, user_id)
    pay_link = my_robokassa.generate_payment_link(my_config.prices[amount], f'Добавление {amount} запросов на аккаунт', pay_id)
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text = "Оплатить сервисом Robokassa", callback_data = f"none", url=pay_link))
    keyboard.add(types.InlineKeyboardButton(text="Проверить статус платежа", callback_data=f"check_{pay_id}"))
    print(f'BUY: {amount}')
    text = f'Пожалуйста, нажмите на кнопку для оплаты\n\n⚠️Важно⚠️\nПосле оплаты обязательно нажмите на кнопку "проверить статус платежа", чтобы запросы пришли на ваш баланс'
    tg_bot.send_message(user_id, text, reply_markup=keyboard)


def handle_check(update, context):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id

    pay_id = int(query.data.split("_")[1])
    amount = int(context.user_data['amount'])
    print(f'CHEK: {amount} / {my_config.prices[amount]}')
    print(my_robokassa.check_payment_status(pay_id))
    print(f'LIMIT: {my_db.get_user_message_limit(user_id) + amount}')
    payment_status, payment_link = my_robokassa.check_payment_status(pay_id)
    my_robokassa_db.set_status_link(pay_id, payment_status, payment_link)

    if payment_status == 100 and context.user_data['pay_id'] != None:
        new_limit = my_db.get_user_message_limit(user_id) + context.user_data['amount']
        my_db.set_user_message_limit(user_id, new_limit)
        del context.user_data['amount']
        context.user_data['pay_id'] = None
        al_mes = my_db.count_all_messages(user_id)
        start = f'✅ Все готово. {amount} запросов начислены на ваш баланс.\n\nТеперь ваш баланс выглядит так:\n\n☑️ Вы можете еще отправить: {new_limit - al_mes} запросов.\n☑️ Всего вы потратили: {al_mes} запросов'

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text = "Продолжить диалог с GPT", callback_data = 'gogpt'))
        tg_bot.send_message(user_id, start, reply_markup = keyboard)
    elif payment_status == 100: tg_bot.send_message(user_id, "Запросы уже зачислены на ваш счёт.")
    else: tg_bot.send_message(user_id, "Оплата не прошла или ожидает выполнения.")


def handle_rating_response(update, context):
    # GOOD
    query = update.callback_query
    query.answer()
    my_db.set_user_rating(query.from_user.id, int(query.data.split('_')[1]))

    start = f'Огромное спасибо за обратную связь! Мы будем становиться лучше с каждым днём 🚀\n\nПожалуйста, в ответном сообщении опишите любые пожелания и ощущения от пользования функционалом бота 🤖'
    query.message.reply_text(start)
    context.user_data['awaiting_review'] = True


def handle_payment(update, context):
    # GOOD
    query = update.callback_query
    query.answer()

    start = 'Нажимая кнопку ниже вы даёте согласие на обработку персональных данных и принимаете условия <a href="https://telegra.ph/Publichnyj-dogovor-oferta-11-29">публичной оферты</a>'
    query.message.reply_text(start, parse_mode='HTML')

    start2 = 'Мы постарались сделать максимально прозрачную систему. Поэтому теперь вам не надо платить никакую подписку. 🤝\n\n☑️ Вы платите исключительно только за запросы.\n☑️ Вы сами контролируете сколько вам нужно.\n\n<i>Если вы хотите приобрести большее количество запросов со скидкой, напишите нам</i> @NeoBoostSupport\n\n👇 Выберите свой пакет запросов 👇'

    keyboard = [
        [InlineKeyboardButton("100 запросов за 200 ₽", callback_data = "buy_100")],
        [InlineKeyboardButton("250 запросов за 425 ₽", callback_data = "buy_250")],
        [InlineKeyboardButton("500 запросов за 750 ₽", callback_data = "buy_500")],
        [InlineKeyboardButton("1000 запросов за 990 ₽", callback_data = "buy_1000")]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    query.message.reply_text(start2, parse_mode = 'HTML', reply_markup = reply_markup)

