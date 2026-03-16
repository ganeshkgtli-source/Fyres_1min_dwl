from cryptography.fernet import Fernet
from django.conf import settings

cipher = Fernet(settings.ENCRYPTION_KEY)


def encrypt_value(value):

    return cipher.encrypt(value.encode()).decode()


def decrypt_value(value):

    return cipher.decrypt(value.encode()).decode()