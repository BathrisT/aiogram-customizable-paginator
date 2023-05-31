import asyncio

from aiogram import Bot, Dispatcher
from aiogram.types import Message

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


async def open_products_list(message: Message):
    paginator = Paginator(
        chat_id=message.chat.id,
        objects=testing_products_database,
        page_size=4,
        get_button_text_from_object_func=lambda obj, index: f'{obj["name"]} | {obj["price"]} руб.',
        get_callback_data_from_object_func=lambda obj, index: f'open_product_{obj["product_id"]}',
        formatted_text_for_page=('*Продукты, доступные в продаже*\n\n'
                                 '___Текущая страница - {page_number} из {pages_count}___')
    )
    await paginator.start(bot_instance=message.bot)


def register_all_handlers(dp):
    register_paginator(dp)
    dp.register_message_handler(open_products_list, commands=['products'])  # Пагинатор открывается по команде /products

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
