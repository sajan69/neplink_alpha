import os
import time
from agora_token_builder import RtcTokenBuilder
from decouple import config

# Agora credentials
APP_ID = config('AGORA_APP_ID')
APP_CERTIFICATE = config('AGORA_APP_CERTIFICATE')

TOKEN_EXPIRATION_TIME = 3600  # 1 hour

def generate_agora_token(channel_name, uid, role):
    """
    Generate an Agora RTC Token for a given user to join a channel.
    :param channel_name: The unique channel name for the call.
    :param uid: User ID for which the token is generated.
    :param role: The role of the user in the call (publisher/subscriber).
    :return: A string token that allows a user to join the Agora channel.
    """
    
    app_id = APP_ID
    app_certificate = APP_CERTIFICATE
    
    role = 1  # Set role as publisher
    expire_time_in_seconds = 3600  # 1 hour validity
    current_timestamp = int(time.time())
    privilege_expired_ts = current_timestamp + expire_time_in_seconds

    token = RtcTokenBuilder.buildTokenWithUid(
        app_id, app_certificate, channel_name, uid, role, privilege_expired_ts
    )
    return token
