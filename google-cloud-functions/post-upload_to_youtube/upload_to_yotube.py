import functions_framework
from flask import Flask, jsonify
import json
import os
import gspread
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv

load_dotenv()

# Define the scopes
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

CONTENT_READY_WORKSHEET = "Content Ready"
PRIORITY_QUEUE_WORKSHEET = "Queue"
YOUTUBE_UNLISTED_WORKSHEET = "Youtube Unlisted"
YOUTUBE_PUBLIC_WORKSHEET = "Youtube Public"

YOUTUBE_UPLOAD = os.getenv("YOUTUBE_UPLOAD")
SERVICE_ACCOUNT_KEY = os.getenv("SERVICE_ACCOUNT_KEY")
print("YOUTUBE_UPLOAD : ", YOUTUBE_UPLOAD)
print("SERVICE_ACCOUNT_KEY : ", SERVICE_ACCOUNT_KEY)



def authenticate_with_user_info(scopes, credentials_info):
    creds = None
    if credentials_info:
        creds = Credentials.from_authorized_user_info(credentials_info, scopes)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print("No valid credentials provided.")
            return None
    return build("youtube", "v3", credentials=creds)



def update_video_privacy(video_id):
    """Update the privacy status of a YouTube video to 'public'."""
    try:
        youtube_credentials_json = YOUTUBE_UPLOAD
        print(f"\nyoutube_credentials_json: {youtube_credentials_json}")

        if not youtube_credentials_json:
            print("Missing environment variables for credentials.")
            return "Error: Missing credentials."
    
        youtube_credentials_info = json.loads(youtube_credentials_json)
        youtube = authenticate_with_user_info(SCOPES, youtube_credentials_info)
        # Get the video details
        response = youtube.videos().list(
            part="status",
            id=video_id
        ).execute()
        
        print("\n", response)
        # Check if the video exists
        if not response["items"]:
            print(f"Video with ID {video_id} not found.")
            return
        
        # Update the video's privacy status to 'public'
        youtube.videos().update(
            part="status",
            body={
                "id": video_id,
                "status": {
                    "privacyStatus": "public"
                }
            }
        ).execute()
        
        print(f"Video with ID {video_id} is now public.")
    
    except HttpError as e:
        print(f"An error occurred: {e}")
        return



def authenticate_get_sheet(sheet_name="Redit Posts"):
    service_account_key = os.getenv("SERVICE_ACCOUNT_KEY")
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    if not service_account_key:
        raise ValueError("SERVICE_ACCOUNT_KEY environment variable is not set or is empty")

    try:
        service_account_info = json.loads(service_account_key)
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON format for SERVICE_ACCOUNT_KEY")

    # Authenticate using the credentials dictionary
    creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
    client = gspread.authorize(creds)
    sheet = client.open(sheet_name)
    return sheet


def update_spread_sheet(video_id):
    sheet = authenticate_get_sheet()
    unlisted_worksheet = sheet.worksheet(YOUTUBE_UNLISTED_WORKSHEET)
    public_worksheet = sheet.worksheet(YOUTUBE_PUBLIC_WORKSHEET)

    video_id_column = 'Video ID'
    post_progress_column = 'Post Progress'
    all_rows = unlisted_worksheet.get_all_records()
    headers = unlisted_worksheet.row_values(1)  # Assuming the first row contains headers
    id_index = headers.index(video_id_column)  # Get the column index for Post Id
    progress_index = headers.index(post_progress_column) 

    # Find the row containing the specified Post Id
    for i, row in enumerate(all_rows, start=2):  # Start at 2 to account for the header row
        if str(row[video_id_column]) == str(video_id):
            row_values = unlisted_worksheet.row_values(i)  # Get the full row's values
            row_values[progress_index] = 'YT_PUBLIC'

            # Append the row to the target sheet
            public_worksheet.append_row(row_values)
            
            # Delete the row from the source sheet
            unlisted_worksheet.delete_rows(i)
            
            print(f"Moved row with Post Id {video_id} from {YOUTUBE_UNLISTED_WORKSHEET} to {YOUTUBE_PUBLIC_WORKSHEET}")
            return True

    print(f"Post Id {video_id} not found in {YOUTUBE_UNLISTED_WORKSHEET}")
    return False

    

def start_video_public_squence(video_id):
    if update_spread_sheet(video_id):
        update_video_privacy(video_id)
        return f"Video id {video_id} successfully made PUBLIC"
    raise ValueError("Video not in UNLISTED Sheet")


@functions_framework.http
def hello_http(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """

    headers = {
        "Access-Control-Allow-Origin": "*",  # Allow all origins
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",  # Allowed methods
        "Access-Control-Allow-Headers": "Content-Type, Authorization",  # Allowed headers
    }

    # Handle preflight OPTIONS request
    if request.method == "OPTIONS":
        return ("", 204, headers)

    if request.method == "POST":
        request_json = request.get_json(silent=True)
        request_args = request.args
        print("request_args : " , request_args, " | request_json : " , request_json)

        if request_json and 'video_id' in request_json:
            video_id = request_json['video_id']
            try:
                message = start_video_public_squence(video_id)  # Custom logic
                data = {"message": message}
                response = jsonify(data)
                response.status_code = 200  # OK
                response.headers.update(headers)  # Add CORS headers
                return response
            except ValueError as e:
                # Handle server errors
                data = {"error": "Video Not found", "details": str(e)}
                response = jsonify(data)
                response.status_code = 400  # Internal Server Error
                return response

    raise "Video ID not given in request"