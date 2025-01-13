import os
import json
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from utils import get_google_service_account_key


class GoogleDrive:
    # Define the Google Drive API scope
    SCOPES = ['https://www.googleapis.com/auth/drive.file']

    def __init__(self):
        pass


    def authenticate_with_service_account(self):
        """Authenticate using the Service Account JSON key."""
        service_account_key = os.environ.get("SERVICE_ACCOUNT_KEY")

        if not service_account_key:
            raise ValueError("SERVICE_ACCOUNT_KEY environment variable is not set or is empty")

        try:
            print("service_account_key " : service_account_key)
            service_account_info = json.loads(service_account_key)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format for SERVICE_ACCOUNT_KEY")
        credentials = service_account.Credentials.from_service_account_info(
            service_account_info, scopes=self.SCOPES
        )
        
        # Build the Drive API client
        drive_service = build('drive', 'v3', credentials=credentials)
        return drive_service


    def create_folder(self, drive_service, folder_name, parent_id=None):
        """Creates a folder on Google Drive and returns the folder ID."""
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        
        if parent_id:
            file_metadata['parents'] = [parent_id]  # Specify the parent folder ID

        folder = drive_service.files().create(body=file_metadata, fields='id').execute()
        print(f"Folder '{folder_name}' created successfully! Folder ID: {folder.get('id')}")
        return folder.get('id')


    def upload_video_to_drive(self, drive_service, video_path, folder_id=None):
        """Uploads a video file to Google Drive using the authenticated service account."""
        # Set up file metadata
        file_metadata = {'name': os.path.basename(video_path)}
        
        if folder_id:
            file_metadata['parents'] = [folder_id]  # Upload to a specific folder
        
        # Prepare the video file for upload
        media = MediaFileUpload(video_path, mimetype='video/mp4', resumable=True)
        
        # Upload the video file
        file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        print(f"Video uploaded successfully! File ID: {file.get('id')}")
        return file.get('id')

# Example usage
# video_path = 'output_video2.mp4'  # Replace with the path to your video file

# # Nested folder structure: "ParentFolder/ChildFolder/GrandchildFolder"
# child_folder_name = 'ChildFolder'
# parent_folder_id = "1PVR606GT6kWsuqGt97mH4NEv3SmvJww5"

# drive = GoogleDrive()

# # Authenticate and get the drive service
# drive_service = drive.authenticate_with_service_account()

# # Create the child folder inside the parent folder
# child_folder_id = drive.create_folder(drive_service, child_folder_name, parent_folder_id)

# # Upload the video to the grandchild folder (nested folder)
# drive.upload_video_to_drive(drive_service, video_path, child_folder_id)
