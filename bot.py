# Основная логика бота
import telebot
import buttons
import database

# Создаем объект бота
bot = telebot.TeleBot('TOKEN')
admins = []
group_id = -1
# Временные данные
users = {}
admin_pr = {} #!!!

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

# Корзина
@bot.callback_query_handler(lambda call: call.data in ['cart', 'order', 'clear'])
def cart_handle(call):
    user_id = call.message.chat.id
    if call.data == 'cart':
        text = 'Ваша корзина:\n\n'
        total = 0
        user_cart = database.show_cart(user_id)
        if user_cart:
            for i in user_cart:
                text += f'Товар: {i[1]}\nКоличество: {i[-1]}\n\n'
                total += database.get_exact_price(i[1]) * i[-1]
            text += f'Итого: {total}сум'
            bot.delete_message(chat_id=user_id, message_id=call.message.message_id)
            bot.send_message(user_id, text, reply_markup=buttons.cart_buttons())
    elif call.data == 'clear':
        bot.delete_message(chat_id=user_id, message_id=call.message.message_id)
        database.clear_cart(user_id)
        bot.send_message(user_id, 'Ваша корзина очищена!',
                         reply_markup=buttons.main_menu(database.get_pr_buttons()))
    elif call.data == 'order':
        text = (f'Новый заказ!\n'
                f'Клиент: @{call.message.chat.username}\n\n')
        total = 0
        user_cart = database.show_cart(user_id)
        for i in user_cart:
            text += f'Товар: {i[1]}\nКоличество: {i[-1]}\n\n'
            total += database.get_exact_price(i[1]) * i[-1]
        text += f'Итого: {total}сум'
        bot.delete_message(chat_id=user_id, message_id=call.message.message_id)
        bot.send_message(user_id, 'Отправьте вашу геолокацию, куда вам доставить заказ!',
                         reply_markup=buttons.loc_button())
        # Переход на этап получения локации
        bot.register_next_step_handler(call.message, get_loc, text)

# Этап получения локации
def get_loc(message, text):
    user_id = message.from_user.id
    # Проверяем правильность отправки геопозиции
    if message.location:
        database.make_order(user_id)
        database.clear_cart(user_id)
        bot.send_message(group_id, text)
        bot.send_location(group_id, longitude=message.location.longitude, latitude=message.location.latitude)
        bot.send_message(user_id, 'Ваш заказ успешно оформлен, с вами скоро свяжутся!',
                         reply_markup=telebot.types.ReplyKeyboardRemove())
        bot.send_message(user_id, 'Выберите пункт меню:',
                         reply_markup=buttons.main_menu(database.get_pr_buttons()))
    else:
        bot.send_message(user_id, 'Отправьте локацию по кнопке!')
        # Возвращаем на этап получения локации
        bot.register_next_step_handler(message, get_loc, text)

# Обработчик команды /admin
@bot.message_handler(commands=['admin'])
def admin(message):
    user_id = message.from_user.id
    if user_id in admins:
        bot.send_message(user_id, 'Добро пожаловать в админ-панель!',
                         reply_markup=buttons.admin_buttons())
        # Переход на этап выбора
        bot.register_next_step_handler(message, get_choice)

# Этап выбора
def get_choice(message):
    user_id = message.from_user.id
    if message.text == 'Добавить продукт':
        bot.send_message(user_id, 'Чтобы добавить товар, впишите следующие данные:\n'
                                  'Название, описание, кол-во на складе, цена, фото\n'
                                  'Пример:\n'
                                  'Картошка фри, свежая и вкусная, 100, 14000, https://fries.jpg\n\n'
                                  'Фото загружать на https://postimages.org/ и присылать прямую ссылку!')
        # Переход на этап получения товара
        bot.register_next_step_handler(message, add_pr)
    elif message.text == 'Удалить продукт':
        if database.check_pr():
            bot.send_message(user_id, 'Выберите товар',
                             reply_markup=buttons.get_admin_pr(database.get_pr_buttons()))
            act = 'del'
            # Переход на этап выбора товара
            bot.register_next_step_handler(message, get_pr, act)
    elif message.text == 'Изменить продукт':
        if database.check_pr():
            bot.send_message(user_id, 'Выберите товар',
                             reply_markup=buttons.get_admin_pr(database.get_pr_buttons()))
            act = 'edit'
            # Переход на этап выбора товара
            bot.register_next_step_handler(message, get_pr, act)
    elif message.text == 'Вернуться в главное меню':
        start(message)

# Этап получения товара
def add_pr(message):
    user_id = message.from_user.id
    product = message.text.split(', ')
    if len(product) == 5:
        database.add_pr_to_db(*product)
        bot.send_message(user_id, 'Товар успешно добавлен!')
    else:
        bot.send_message(user_id, 'Данные неверны!')
        # Возвращаем на этап получения товара
        bot.register_next_step_handler(message, add_pr)

# Этап выбора товара
def get_pr(message, act):
    user_id = message.from_user.id
    product_name = message.text
    if act == 'del':
        database.del_from_db(product_name)
        bot.send_message(user_id, 'Товар удален!',
                         reply_markup=buttons.admin_buttons())
        # Переход на этап выбора
        bot.register_next_step_handler(message, get_choice)
    elif act == 'edit':
        admin_pr[user_id] = product_name #!!!
        bot.send_message(user_id, 'Выберите атрибут, который надо изменить!',
                         reply_markup=telebot.types.ReplyKeyboardRemove())
        bot.send_message(user_id, 'Список атрибутов:',
                         reply_markup=buttons.attr_buttons())

# Обработчик выбора атрибута
@bot.callback_query_handler(lambda call: call.data in ['pr_name', 'pr_des', 'pr_count', 'pr_price', 'pr_photo'])
def edit_product(call):
    user_id = call.message.chat.id
    if call.data == 'pr_count':
        bot.delete_message(chat_id=user_id, message_id=call.message.message_id)
        bot.send_message(user_id, 'Чтобы добавить товар, напишите +количество, а если убавить, то -количество.\n'
                                   'Пример: +15 или -15')
        # Переход на этап изменения
        bot.register_next_step_handler(call.message, confirm_edit, attr=call.data, act='count')
    else:
        bot.delete_message(chat_id=user_id, message_id=call.message.message_id)
        bot.send_message(user_id, 'Введите новое значение!')
        # Переход на этап изменения
        bot.register_next_step_handler(call.message, confirm_edit, attr=call.data, act='')

# Этап изменения
def confirm_edit(message, attr, act):
    user_id = message.from_user.id
    if act == 'count':
        database.change_pr(admin_pr[user_id], int(message.text[1:]), attr, message.text[0]) #!!!
        bot.send_message(user_id, 'Изменение прошло успешно!',
                         reply_markup=buttons.admin_buttons())
        # Переход на этап выбора
        bot.register_next_step_handler(message, get_choice)
    else:
        if attr == 'pr_price':
            database.change_pr(admin_pr[user_id], int(message.text), attr) #!!!
        else:
            database.change_pr(admin_pr[user_id], message.text, attr) #!!!
        bot.send_message(user_id, 'Изменение прошло успешно!',
                         reply_markup=buttons.admin_buttons())
        # Переход на этап выбора
        bot.register_next_step_handler(message, get_choice)

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

# Запуск бота
bot.polling(non_stop=True)
