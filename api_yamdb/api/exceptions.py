from rest_framework.exceptions import APIException


class UserNotExistsError(APIException):
    status_code = 404
    default_detail = (
        'Пользователь не найден'
    )
    default_code = 'user_not_exists'
