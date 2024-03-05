import random

CONFIRMATION_CODE_LENGTH = 20
CONFIRMATION_CODE_CHARACTERS = '1234567890'


def get_confirmation_code():
    return ''.join(
        random.choices(
            CONFIRMATION_CODE_CHARACTERS,
            k=CONFIRMATION_CODE_LENGTH
        )
    )

print(get_confirmation_code())
