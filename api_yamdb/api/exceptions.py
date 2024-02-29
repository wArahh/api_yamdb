from rest_framework.exceptions import APIException


class UserNotExistsError(APIException):
    status_code = 404
    default_detail = (
        'Пользователь не найден'
    )
    default_code = 'user_not_exists'


class EmailExistsError(APIException):
    status_code = 400
    default_detail = (
        'Пользователь с таким email уже существует'
    )
    default_code = 'email_exists_error'


class PutMethodError(APIException):
    status_code = 405
    default_detail = (
        'PUT метод по данному эндпоинту недоступен'
    )
    default_code = 'put_method_error'
