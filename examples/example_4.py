import asyncio

from aiogram import Bot, Dispatcher
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from aiogram_customizable_paginator.pagination import register_paginator, Paginator

testing_products_database = [
    {'product_id': 1, 'name': 'Pencil', 'price': 0},
    {'product_id': 2, 'name': 'Notebook', 'price': 1000},
    {'product_id': 3, 'name': 'Eraser', 'price': 50},
    {'product_id': 4, 'name': 'Marker', 'price': 150},
    {'product_id': 5, 'name': 'Highlighter', 'price': 200},
    {'product_id': 6, 'name': 'Ruler', 'price': 100},
    {'product_id': 7, 'name': 'Stapler', 'price': 500},
    {'product_id': 8, 'name': 'Tape', 'price': 150},
    {'product_id': 9, 'name': 'Glue', 'price': 200},
    {'product_id': 10, 'name': 'Scissors', 'price': 300},
    {'product_id': 11, 'name': 'Calculator', 'price': 1000},
    {'product_id': 12, 'name': 'Pen', 'price': 50},
    {'product_id': 13, 'name': 'Folder', 'price': 300},
    {'product_id': 14, 'name': 'Binder', 'price': 600},
    {'product_id': 15, 'name': 'Paper Clips', 'price': 50},
]

testing_products_database2 = [
    {'product_id': 16, 'name': 'History Textbook', 'price': 1500},
    {'product_id': 17, 'name': 'Math Textbook', 'price': 2000},
    {'product_id': 18, 'name': 'Science Textbook', 'price': 2500},
    {'product_id': 19, 'name': 'Language Arts Textbook', 'price': 1800},
    {'product_id': 20, 'name': 'Art Textbook', 'price': 2200},
    {'product_id': 21, 'name': 'Music Textbook', 'price': 1900},
    {'product_id': 22, 'name': 'Physical Education Textbook', 'price': 1700},
    {'product_id': 23, 'name': 'Computer Science Textbook', 'price': 3500},
    {'product_id': 24, 'name': 'Social Studies Textbook', 'price': 2100},
    {'product_id': 25, 'name': 'Foreign Language Textbook', 'price': 2400}
]

async def open_list_selector_by_command(message: Message):
    text = 'Выберите список'
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('Канцтовары', callback_data='products_1')],
        [InlineKeyboardButton('Учебники', callback_data='products_2')]
    ])
    await message.bot.send_message(chat_id=message.chat.id, text=text, reply_markup=kb)

async def open_list_selector_by_callback(callback: CallbackQuery):
    text = 'Выберите список'
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('Канцтовары', callback_data='products_1')],
        [InlineKeyboardButton('Учебники', callback_data='products_2')]
    ])
    await callback.bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        text=text,
        reply_markup=kb
    )


async def open_products_list1(callback: CallbackQuery):
    paginator = Paginator(
        objects=testing_products_database,
        page_size=4,
        get_row_text_from_object_func=lambda obj, index: f'*{index + 1}.* {obj["name"]} - {obj["price"]} руб.',
        formatted_text_for_page=('*Список канцтоваров доступных в продаже:*\n\n'
                                 '{rows_text}\n'
                                 '___Текущая страница - {page_number} из {pages_count}___'),
        ending_kb_elements=[[InlineKeyboardButton(text='Назад', callback_data='products_list')]]
    )
    await paginator.edit_message(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        bot_instance=callback.bot
    )

async def open_products_list2(callback: CallbackQuery):
    paginator = Paginator(
        objects=testing_products_database,
        page_size=4,
        get_row_text_from_object_func=lambda obj, index: f'*{index + 1}.* {obj["name"]} - {obj["price"]} руб.',
        formatted_text_for_page=('*Список учебников доступных в продаже:*\n\n'
                                 '{rows_text}\n'
                                 '___Текущая страница - {page_number} из {pages_count}___'),
        ending_kb_elements=[[InlineKeyboardButton(text='Назад', callback_data='products_list')]]
    )

    await paginator.edit_message(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        bot_instance=callback.bot
    )


def register_all_handlers(dp):
    register_paginator(dp)
    dp.register_message_handler(open_list_selector_by_command, commands=['products'])  # Пагинатор открывается по команде /products
    dp.register_callback_query_handler(open_list_selector_by_callback, lambda callback: callback.data == 'products_list')
    dp.register_callback_query_handler(open_products_list1, lambda callback: callback.data == 'products_1')
    dp.register_callback_query_handler(open_products_list2, lambda callback: callback.data == 'products_2')


async def main():
    bot = Bot(token='YOUR_BOT_TOKEN')  # TODO: При тестировании заменяем бот токен на свой

    dp = Dispatcher(bot)

    register_all_handlers(dp)

    try:
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())
