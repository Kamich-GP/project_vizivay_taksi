# Кнопки
from telebot import types


# Кнопка отправки номера
def num_button():
    # Создаем пространство
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # Создаем сами кнопки
    but1 = types.KeyboardButton('Отправить номер📞',
                                request_contact=True)
    # Добавляем кнопки в пространство
    kb.add(but1)
    return kb

# Кнопки вывода товаров
def main_menu(products):
    # Создаем пространство
    kb = types.InlineKeyboardMarkup(row_width=2)
    # Создаем сами кнопки
    cart = types.InlineKeyboardButton(text='Корзина🛒', callback_data='cart')
    all_products = [types.InlineKeyboardButton(text=i[1], callback_data=i[0])
                    for i in products]
    # Добавляем кнопки в пространство
    kb.add(*all_products)
    kb.row(cart)
    return kb

# Кнопка "Назад"
def back_button():
    # Создаем пространство
    kb = types.InlineKeyboardMarkup(row_width=1)
    # Создаем саму кнопку
    but1 = types.InlineKeyboardButton(text='Назад🔙', callback_data='back')
    # Добавляем кнопку в пространство
    kb.add(but1)
    return kb

# Кнопки выбора кол-ва товара
def choose_count_buttons(pr_count, plus_or_minus='', amount=1):
    # Создаем пространство
    kb = types.InlineKeyboardMarkup(row_width=3)
    # Создаем сами кнопки
    plus = types.InlineKeyboardButton(text='+', callback_data='increment')
    minus = types.InlineKeyboardButton(text='-', callback_data='decrement')
    count = types.InlineKeyboardButton(text=str(amount), callback_data=str(amount))
    back = types.InlineKeyboardButton(text='Назад🔙', callback_data='back')
    to_cart = types.InlineKeyboardButton(text='В корзину🛒', callback_data='to_cart')
    # Алгоритм изменения кол-ва
    if plus_or_minus == 'increment':
        if amount < pr_count:
            count = types.InlineKeyboardButton(text=str(amount+1), callback_data=str(amount))
    elif plus_or_minus == 'decrement':
        if 1 < amount:
            count = types.InlineKeyboardButton(text=str(amount-1), callback_data=str(amount))
    # Добавляем сами кнопки
    kb.add(minus, count, plus, back, to_cart)
    return kb

# Кнопки корзины
def cart_buttons():
    # Создаем пространство
    kb = types.InlineKeyboardMarkup(row_width=2)
    # Создаем сами кнопки
    clear = types.InlineKeyboardButton(text='Очистить корзину🗑️', callback_data='clear')
    order = types.InlineKeyboardButton(text='Оформить заказ🧾', callback_data='order')
    back = types.InlineKeyboardButton(text='Назад🔙', callback_data='back')
    # Добавляем кнопки в пространство
    kb.add(clear, order, back)
    return kb

# Кнопка отправки локации
def loc_button():
    # Создаем пространство
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # Создаем сами кнопки
    but1 = types.KeyboardButton('Отправить геопозицию📍',
                                request_location=True)
    # Добавляем кнопки в пространство
    kb.add(but1)
    return kb

# Кнопки меню администратора
def admin_buttons():
    # Создаем пространство
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # Создаем сами кнопки
    but1 = types.KeyboardButton('Добавить продукт')
    but2 = types.KeyboardButton('Удалить продукт')
    but3 = types.KeyboardButton('Изменить продукт')
    but4 = types.KeyboardButton('Вернуться в главное меню')
    # Добавляем кнопки в пространство
    kb.add(but1, but2, but3, but4)
    return kb

# Кнопки выбора товара для администратора
def get_admin_pr(products):
    # Создаем пространство
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # Создаем сами кнопки
    all_products = [types.KeyboardButton(i[1]) for i in products]
    back = types.KeyboardButton('Назад')
    # Добавляем кнопки в пространство
    kb.add(*all_products)
    kb.row(back)
    return kb

# Кнопки выбора атрибута товара
def attr_buttons():
    # Создаем пространство
    kb = types.InlineKeyboardMarkup(row_width=2)
    # Создаем сами кнопки
    but1 = types.InlineKeyboardButton(text='Название', callback_data='pr_name')
    but2 = types.InlineKeyboardButton(text='Описание', callback_data='pr_des')
    but3 = types.InlineKeyboardButton(text='Количество', callback_data='pr_count')
    but4 = types.InlineKeyboardButton(text='Цена', callback_data='pr_price')
    but5 = types.InlineKeyboardButton(text='Фото', callback_data='pr_photo')
    # Добавляем кнопки в пространство
    kb.add(but1, but2, but3, but4, but5)
    return kb
