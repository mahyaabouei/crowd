
from . import serializers
from cryptography.fernet import Fernet
import base64
from . import models
from ast import literal_eval
from datetime import datetime, timedelta
import json
from django.core.exceptions import ObjectDoesNotExist

def encryptionUser(user):
    user = serializers.UserSerializer(user).data
    user['created_at'] = datetime.utcnow().isoformat()  
    user = json.dumps(user)
    # user = str(user)
    with open('secret.key', 'rb') as key_file:
        key = key_file.read()
    fernet = Fernet(key)
    token = fernet.encrypt(user.encode())
    token = base64.urlsafe_b64encode(token).decode()
    return token

def is_token_blacklisted(token):
    black_list = models.BlacklistedToken.objects.filter(token=token)
    if black_list.exists() :
        return True
    return False
def decryptionUser(Bearer):
    try:
        token = Bearer.split('Bearer ')[1]
        if is_token_blacklisted(token):
            print("Token is blacklisted.")
            return None
        with open('secret.key', 'rb') as key_file:
            key = key_file.read()
        fernet = Fernet(key)
        encrypted_bytes = base64.urlsafe_b64decode(token.encode())
        user_data = fernet.decrypt(encrypted_bytes).decode()
        user_data = json.loads(user_data)  

        created_at = datetime.fromisoformat(user_data['created_at'])
        if datetime.utcnow() - created_at > timedelta(hours=24): 
            print("Token has expired.")
            return None
        
        user = models.User.objects.filter(id=user_data['id'])
        return user
    except Exception as e:
        print(f"Decryption or user retrieval failed: {e}")
        return None




def encryptionadmin(admin):
    admin = serializers.AdminSerializer(admin).data
    admin['created_at'] = datetime.utcnow().isoformat()  
    admin = json.dumps(admin)
    with open('secret.key', 'rb') as key_file:
        key = key_file.read()
    fernet = Fernet(key)
    token = fernet.encrypt(admin.encode())
    token = base64.urlsafe_b64encode(token).decode()
    return token

def decryptionadmin(Bearer):
    try:
        token = Bearer.split('Bearer ')[1]
        if is_token_blacklisted(token):
            print("Token is blacklisted.")
            return None

        with open('secret.key', 'rb') as key_file:
            key = key_file.read()
        fernet = Fernet(key)
        encrypted_bytes = base64.urlsafe_b64decode(token.encode())
        admin_data = fernet.decrypt(encrypted_bytes).decode()
        admin_data = json.loads(admin_data)  

        created_at = datetime.fromisoformat(admin_data['created_at'])
        if datetime.utcnow() - created_at > timedelta(hours=24):  
            print("Token has expired.")
            return None
        
        admin = models.Admin.objects.filter(id=admin_data['id'])
        return admin
    except Exception as e:
        print(f"Decryption or user retrieval failed: {e}")
        return None




