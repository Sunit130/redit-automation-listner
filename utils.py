import os
import json


def get_google_service_account_key():
    service_account_key = os.environ.get("SERVICE_ACCOUNT_KEY")
    credentials = json.loads(service_account_key)
    return credentials
