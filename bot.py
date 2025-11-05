# Основная логика бота
import telebot
import buttons
import database

# Создаем объект бота
bot = telebot.TeleBot('TOKEN')
# Временные данные
users = {}

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    # Проверяем пользователя на наличие в БД
    if database.check_user(user_id):
        bot.send_message(user_id, 'Добро пожаловать!',
                         reply_markup=telebot.types.ReplyKeyboardRemove())
        bot.send_message(user_id, 'Выберите пункт меню:',
                         reply_markup=buttons.main_menu(database.get_pr_buttons()))
    else:
        bot.send_message(user_id,
                         'Давайте начнем регистрацию, напишите свое имя!',
                         reply_markup=telebot.types.ReplyKeyboardRemove())
        # Переход на этап получения имени
        bot.register_next_step_handler(message, get_name)

# Этап получения имени
def get_name(message):
    user_id = message.from_user.id
    user_name = message.text
    bot.send_message(user_id, 'Отлично, теперь отправьте свой номер телефона!',
                     reply_markup=buttons.num_button())
    # Этап получения номера
    bot.register_next_step_handler(message, get_num, user_name)

# Этап получения номера
def get_num(message, user_name):
    user_id = message.from_user.id
    # Проверяем правильность номера телефона
    if message.contact:
        user_num = message.contact.phone_number
        database.register(user_id, user_name, user_num)
        bot.send_message(user_id, 'Регистрация прошла успешно!')
        start(message)
    else:
        bot.send_message(user_id, 'Отправьте номер по кнопке!')
        # Возвращение на этап получения номера
        bot.register_next_step_handler(message, get_num, user_name)

# Выбор кол-ва товара
@bot.callback_query_handler(lambda call: call.data in ['increment', 'decrement', 'to_cart', 'back'])
def choose_pr_count(call):
    user_id = call.message.chat.id
    if call.data == 'increment':
        user_count = users[user_id]['product_count'] # Достаем сколько товара берет user
        stock = database.get_exact_pr(users[user_id]['product_name'])[3] # Кол-во товара на складе
        if user_count < stock:
            bot.edit_message_reply_markup(chat_id=user_id, message_id=call.message.message_id,
                                          reply_markup=buttons.choose_count_buttons(stock,
                                                                                    'increment',
                                                                                    user_count))
            users[user_id]['product_count'] += 1
    elif call.data == 'decrement':
        user_count = users[user_id]['product_count'] # Достаем сколько товара берет user
        stock = database.get_exact_pr(users[user_id]['product_name'])[3] # Кол-во товара на складе
        if 1 < user_count:
            bot.edit_message_reply_markup(chat_id=user_id, message_id=call.message.message_id,
                                          reply_markup=buttons.choose_count_buttons(stock,
                                                                                    'decrement',
                                                                                    user_count))
            users[user_id]['product_count'] -= 1
    elif call.data == 'back':
        bot.delete_message(chat_id=user_id, message_id=call.message.message_id)
        bot.send_message(user_id, 'Выберите пункт меню:',
                         reply_markup=buttons.main_menu(database.get_pr_buttons()))
    elif call.data == 'to_cart':
        user_product = database.get_exact_pr(users[user_id]['product_name'])[1] # Название товара
        user_count = users[user_id]['product_count'] # Сколько товара берет user
        database.add_to_cart(user_id, user_product, user_count)
        bot.delete_message(chat_id=user_id, message_id=call.message.message_id)
        bot.send_message(user_id, 'Товар успешно помещен в корзину!',
                         reply_markup=buttons.main_menu(database.get_pr_buttons()))

# Выбор товара
@bot.callback_query_handler(lambda call: int(call.data) in [i[0] for i in database.get_all_pr()])
def choose_product(call):
    user_id = call.message.chat.id
    # Достаем данные о продукте из БД
    pr_info = database.get_exact_pr(int(call.data))
    if pr_info[3] > 0:
        bot.delete_message(chat_id=user_id, message_id=call.message.message_id)
        bot.send_photo(user_id, photo=pr_info[-1], caption=f'{pr_info[1]}\n\n'
                                  f'Описание: {pr_info[2]}\n'
                                  f'Кол-во: {pr_info[3]}\n'
                                  f'Цена: {pr_info[4]}сум',
                       reply_markup=buttons.choose_count_buttons(pr_info[3]))
        users[user_id] = {'product_name': pr_info[0], 'product_count': 1}
    else:
        bot.delete_message(chat_id=user_id, message_id=call.message.message_id)
        bot.send_photo(user_id, photo=pr_info[-1], caption=f'{pr_info[1]}\n\n'
                                                           f'Описание: {pr_info[2]}\n'
                                                           f'Кол-во: НЕТ В НАЛИЧИИ\n'
                                                           f'Цена: {pr_info[4]}сум',
                       reply_markup=buttons.back_button())

# Обработчик команды /admin
@bot.message_handler(commands=['admin'])
def admin(message):
    user_id = message.from_user.id
    bot.send_message(user_id, 'Чтобы добавить товар, впишите следующие данные:\n'
                                'Название, описание, кол-во на складе, цена, фото\n'
                                'Пример:\n'
                                'Картошка фри, свежая и вкусная, 100, 14000, https://fries.jpg\n\n'
                                'Фото загружать на https://postimages.org/ и присылать прямую ссылку!')
    # Переход на этап получения товара
    bot.register_next_step_handler(message, add_pr)

# Этап получения товара
def add_pr(message):
    user_id = message.from_user.id
    product = message.text.split(', ')
    database.add_pr_to_db(*product)
    bot.send_message(user_id, 'Товар успешно добавлен!')

# Запуск бота
bot.polling(non_stop=True)
