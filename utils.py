import os
import json
import shutil

def print_storage_info():
    # Get disk usage statistics
    total, used, free = shutil.disk_usage("/")
    
    # Convert bytes to MB
    total_mb = total / (1024**2)
    used_mb = used / (1024**2)
    free_mb = free / (1024**2)
    
    print(f"Total Storage: {total_mb:.2f} MB")
    print(f"Used Storage: {used_mb:.2f} MB")
    print(f"Free Storage: {free_mb:.2f} MB")


def get_google_service_account_key():
    service_account_key = os.environ.get("SERVICE_ACCOUNT_KEY")
    credentials = json.loads(service_account_key)
    return credentials
