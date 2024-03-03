from rest_framework.exceptions import APIException

NOT_FOUND_EMAIL = 'Пользователь с таким email уже существует'


class EmailExistsError(APIException):
    status_code = 400
    default_detail = (
        NOT_FOUND_EMAIL
    )
    default_code = 'email_exists_error'
