"""
WSGI config for neplink project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
import base64
import sys
from pathlib import Path

# Set up BASE_DIR to match settings.py
BASE_DIR = Path(__file__).resolve().parent.parent
print(f"Base directory: {BASE_DIR}")

# Setup Firebase credentials from environment variable if available
firebase_credentials_env = os.environ.get('FIREBASE_CREDENTIALS')
if firebase_credentials_env:
    try:
        # Use the same path as defined in settings.py
        firebase_creds_path = os.path.join(BASE_DIR, 'firebase_credentials.json')
        print(f"Writing Firebase credentials to: {firebase_creds_path}")
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(firebase_creds_path), exist_ok=True)
        
        # Decode and write the credentials
        with open(firebase_creds_path, 'wb') as f:
            decoded_creds = base64.b64decode(firebase_credentials_env)
            f.write(decoded_creds)
            print(f"Firebase credentials successfully written ({len(decoded_creds)} bytes)")
        
        # Verify the file exists
        if os.path.exists(firebase_creds_path):
            print(f"Verified: Firebase credentials file exists at {firebase_creds_path}")
        else:
            print(f"ERROR: Firebase credentials file was not created at {firebase_creds_path}")
    except Exception as e:
        print(f"Error setting up Firebase credentials: {e}", file=sys.stderr)
else:
    print("WARNING: FIREBASE_CREDENTIALS environment variable not found")

# Now proceed with normal WSGI application setup
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'neplink.settings')

application = get_wsgi_application()

app = application
