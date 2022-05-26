import datetime
import jwt
from django.conf import settings

private_key = settings.PKEY
public_key = settings.PBKEY

def generate_access_token(user):

    access_token_payload = {
        'token_type' : "access",
        'user_id' : user.id,
        'user_email' : user.email,
        'username': user.username,
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes = 50),
    }
    access_token = jwt.encode(access_token_payload,bytes(private_key , 'utf-8'), algorithm='RS256')
    return access_token


def generate_refresh_token(user):
    
    refresh_token_payload = {
        'token_type' : "refresh",
        'user_id' : user.id,
        'user_email' : user.email,
        'username': user.username,
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7),
    }

    refresh_token = jwt.encode(refresh_token_payload, bytes(private_key , 'utf-8'), algorithm='RS256')

    return refresh_token
