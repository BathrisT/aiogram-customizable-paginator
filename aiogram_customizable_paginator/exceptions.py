class PaginatorException(Exception):
    """Общая ошибка"""

class PaginatorNotFound(PaginatorException):
    """Ошибка, которая вызывается когда идет попытка обратиться к пагинатору, объект которого уже не существует"""
