from typing import Callable, Any, Optional, List, TypeVar

from aiogram import Dispatcher, Bot
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from .exceptions import PaginatorNotFound

_Self = TypeVar('_Self', bound='Paginator')

class Paginator:

    created_paginators_by_data: dict[tuple[int, int], _Self] = dict()

    def __init__(
            self,
            chat_id: int,
            objects: list[Any],
            get_row_text_from_object_func: Optional[Callable[[Any, int], str]] = None,
            get_button_text_from_object_func: Optional[Callable[[Any, int], str]] = None,
            get_callback_data_from_object_func: Optional[Callable[[Any, int], str]] = None,
            formatted_text_for_page: str = 'Страница {page_number} из {pages_count}',
            page_size: int = 15,
            buttons_row_size: int = 1,
            symbol_left: str = '«',
            symbol_right: str = '»',
            symbol_fill: str = '•',
            formatted_text_for_button_of_current_page: str = ' {page_number} / {pages_count}',
            parse_mode: str = 'MARKDOWN',
            ending_kb_elements: List[List[InlineKeyboardButton]] = None
    ):
        """
        :param chat_id: id чата, в который будем отправлять пагинатор
        :param objects: объекты которые будут использоваться в отображении на странице

        :param get_row_text_from_object_func: функция получения строки из объекта.
        Первым параметром принимает объект (из :parameter objects), вторым - индекс этого объекта
        :param get_button_text_from_object_func: функция получения строки, которая будет отображаться в кнопке
        из объекта. Первым параметром принимает объект, вторым - индекс этого объекта
        :param get_callback_data_from_object_func: функция получения callback-данных.
        Первым параметром принимает объект, вторым - индекс этого объекта

        :param formatted_text_for_page: текст, который будет отображаться в сообщении, применяться с функцией .format().
        В .format передаются такие аргументы:
        rows_text - сформированный текст с строками для отображения на странице
        page_number - номер текущей страницы
        pages_count - количество страниц

        :param formatted_text_for_button_of_current_page: текст, который будет отображаться на средней кнопке пагинатора,
        применяться с функцией .format(). В .format передаются такие аргументы:
        page_number - номер текущей страницы
        pages_count - количество страниц

        :param page_size: количество элементов на странице
        :param buttons_row_size: количество элементов в строке кнопок
        :param symbol_left: символ перехода на пред страницу
        :param symbol_right: символ перехода на след страницу
        :param symbol_fill: символ заполнения, который применяется когда нельзя листнуть влево или вправо
        """
        self._objects = objects
        self._get_row_text_from_object_func = get_row_text_from_object_func
        self._get_button_text_from_object_func = get_button_text_from_object_func
        self._get_callback_data_from_object_func = get_callback_data_from_object_func
        self._formatted_text_for_page = formatted_text_for_page

        self.page_size = page_size
        self._buttons_row_size = buttons_row_size

        self._symbol_left = symbol_left
        self._symbol_right = symbol_right
        self._symbol_fill = symbol_fill
        self._formatted_text_for_button_of_current_page = formatted_text_for_button_of_current_page

        self._parse_mode = parse_mode

        self._chat_id = chat_id
        self._message_id = None

        self.current_page = 0
        self.pages_count = (len(self._objects) + self.page_size - 1) // self.page_size

        if not ending_kb_elements: ending_kb_elements = []
        self._ending_kb_elements = ending_kb_elements

    def _get_objects_on_current_page(self):
        return self._objects[self.current_page * self.page_size: (self.current_page + 1) * self.page_size]

    def _get_text_from_of_objects_on_current_page(self):
        s = ''
        if self._get_row_text_from_object_func:
            for i, obj in enumerate(self._get_objects_on_current_page()):
                s += self._get_row_text_from_object_func(obj, i + self.current_page * self.page_size) + '\n'
        return s

    def _get_text_for_message(self) -> str:
        return self._formatted_text_for_page.format(
            rows_text=self._get_text_from_of_objects_on_current_page(),
            page_number=self.current_page + 1,
            pages_count=self.pages_count,
        )

    def _get_kb_paginator_elements(self):
        keyboard = []
        if self.current_page == 0:
            keyboard.append(InlineKeyboardButton(self._symbol_fill, callback_data='paginator_nothing'))
        else:
            keyboard.append(InlineKeyboardButton(
                self._symbol_left, callback_data=f'paginator_open_page_{self.current_page - 1}'))

        keyboard.append(InlineKeyboardButton(self._formatted_text_for_button_of_current_page.format(
            page_number=(self.current_page + 1),
            pages_count=self.pages_count
        ), callback_data='paginator_nothing'))

        if self.current_page + 1 < self.pages_count:
            keyboard.append(InlineKeyboardButton(self._symbol_right, callback_data=f'paginator_open_page_{self.current_page + 1}'))
        else:
            keyboard.append(InlineKeyboardButton(self._symbol_fill, callback_data='paginator_nothing'))
        return keyboard

    def _get_keyboard_for_message(self):

        kb = []
        if self._get_button_text_from_object_func and self._get_callback_data_from_object_func:
            current_row = list()
            for i, obj in enumerate(self._get_objects_on_current_page()):
                if len(current_row) == self._buttons_row_size:
                    kb.append(current_row)
                    current_row = list()
                current_row.append(
                    InlineKeyboardButton(
                        text=self._get_button_text_from_object_func(obj, i + self.current_page * self.page_size),
                        callback_data=self._get_callback_data_from_object_func(obj, i + self.current_page * self.page_size)
                    )
                )
            if current_row:
                kb.append(current_row)

        kb += [self._get_kb_paginator_elements()]
        kb += self._ending_kb_elements

        return InlineKeyboardMarkup(inline_keyboard=kb)

    async def start(
            self,
            bot_instance: Bot
    ) -> Message:
        text = self._get_text_for_message()
        kb = self._get_keyboard_for_message()
        sent_message = await bot_instance.send_message(
            chat_id=self._chat_id,
            text=text,
            parse_mode=self._parse_mode,
            reply_markup=kb,
            disable_web_page_preview=True
        )
        self._message_id = sent_message.message_id
        self.__class__.created_paginators_by_data[(self._chat_id, sent_message.message_id)] = self
        return sent_message

    async def _open_page_by_number(self, page_number: int, bot_instance: Bot) -> Message:
        self.current_page = page_number

        text = self._get_text_for_message()
        kb = self._get_keyboard_for_message()
        return await bot_instance.edit_message_text(
            chat_id=self._chat_id,
            message_id=self._message_id,
            text=text,
            parse_mode=self._parse_mode,
            reply_markup=kb,
            disable_web_page_preview=True
        )

    @classmethod
    def get_paginator_object_by_data(cls, user_id: int, message_id: int) -> _Self:
        if (user_id, message_id) not in cls.created_paginators_by_data:
            raise PaginatorNotFound(f'Paginator with user_id={user_id} and message_id={message_id} not found')
        return cls.created_paginators_by_data[(user_id, message_id)]

    @classmethod
    async def open_paginator_other_page_by_callback(cls, callback: CallbackQuery):
        paginator = cls.get_paginator_object_by_data(
            user_id=callback.from_user.id,
            message_id=callback.message.message_id
        )
        await paginator._open_page_by_number(page_number=int(callback.data.split('_')[-1]), bot_instance=callback.bot)


def register_paginator(dp: Dispatcher):
    dp.register_callback_query_handler(
        Paginator.open_paginator_other_page_by_callback,
        lambda callback: callback.data.startswith('paginator_open_page_')
    )
