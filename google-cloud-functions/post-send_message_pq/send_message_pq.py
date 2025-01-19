from datetime import datetime
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


def send_message_pq(post):
    sheet = authenticate_get_sheet()
    content_ready_worksheet = sheet.worksheet(CONTENT_READY_WORKSHEET)
    priority_queue_worksheet = sheet.worksheet(PRIORITY_QUEUE_WORKSHEET)
    
    all_rows = content_ready_worksheet.get_all_records()
    post_in_content_ready = None
    for i, row in enumerate(all_rows, start=2):
        if row['Post ID'] == post['Post ID']:
            post_in_content_ready = row
            content_ready_worksheet.delete_rows(i)
            break

    if post_in_content_ready == None:
        print("post not available in content queue")
        raise ValueError("Post not in content worksheet")


    priority_queue_worksheet_cols = [
        "Priority",	"Date Time", "Post ID", "Post Date", "Post Sub-Reddit",	"Post Progress",\
        "Post Score", "Post Normalized Score",	"Post Title", "Post Content", "Post Content Length",\
        "Post Revised Title",	"Post Revised Content",	"Post Revised Content Length", "Post Character", "Post Link",	"Video ID"
    ]
    msg_priority = 1
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    queue_message = []
    for col in priority_queue_worksheet_cols:
        if col == "Priority":
            queue_message.append(msg_priority)
        elif col == "Date Time":
            queue_message.append(current_date)
        elif col == "Post Revised Title":
            queue_message.append(post["Post Revised Title"])
        elif col == "Post Revised Content":
            queue_message.append(post["Post Revised Content"])
        elif col == "Post Revised Content Length":
            queue_message.append(len(post["Post Revised Content"]))
        else:
            queue_message.append(post_in_content_ready[col])

    priority_queue_worksheet.append_row(queue_message)

    print(f"Post is pushed to Priority queue")
    return "Post is pushed to Priority queue"


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

        if request_json and 'post' in request_json:
            post = request_json['post']
            try:
                message = send_message_pq(post)  # Custom logic
                data = {"message": message}
                response = jsonify(data)
                response.status_code = 200  # OK
                response.headers.update(headers)  # Add CORS headers
                return response
            except ValueError as e:
                # Handle server errors
                data = {"error": "Post not found", "details": str(e)}
                response = jsonify(data)
                response.status_code = 400  # Internal Server Error
                return response

    raise "Unexpected error occured"


