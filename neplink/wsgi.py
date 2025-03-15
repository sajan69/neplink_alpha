"""
WSGI config for neplink project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
import base64

# Setup Firebase credentials from environment variable if available
firebase_credentials_env = os.environ.get('FIREBASE_CREDENTIALS')
if firebase_credentials_env:
    try:
        # Decode the base64 encoded credentials and save to file
        firebase_creds_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'firebase_credentials.json')
        with open(firebase_creds_path, 'wb') as f:
            f.write(base64.b64decode(firebase_credentials_env))
        print(f"Firebase credentials successfully written to {firebase_creds_path}")
    except Exception as e:
        print(f"Error setting up Firebase credentials: {e}")

# Now proceed with normal WSGI application setup
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'neplink.settings')

application = get_wsgi_application()

app = application
