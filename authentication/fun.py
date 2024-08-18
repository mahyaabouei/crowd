
from . import serializers
from cryptography.fernet import Fernet
import base64
from . import models
from ast import literal_eval



def encryptionUser(user):
    user = serializers.UserSerializer(user).data
    user = str(user)
    with open('secret.key', 'rb') as key_file:
        key = key_file.read()
    fernet = Fernet(key)
    token = fernet.encrypt(user.encode())
    token = base64.urlsafe_b64encode(token).decode()
    return token

def decryptionUser(Bearer):
    try:
        token = Bearer.split('Bearer ')[1]
        with open('secret.key', 'rb') as key_file:
            key = key_file.read()
        fernet = Fernet(key)
        encrypted_bytes = base64.urlsafe_b64decode(token.encode())
        user = fernet.decrypt(encrypted_bytes).decode()
        user = literal_eval(user)
        user = models.User.objects.filter(id=user['id'])
        return user
    except:
        return None




