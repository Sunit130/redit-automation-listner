import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import json
import os

class PriorityQueue:
    def __init__(self, sheet_name, worksheet_name="Queue"):
        # Authenticate and initialize the Google Sheet
        service_account_key = os.environ.get("SERVICE_ACCOUNT_KEY")
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]
        self.headers = [
            'Priority',
            'Date Time',
            'Post ID',
            'Post Date',
            'Post Sub-Reddit',
            'Post Progress',
            'Post Score',
            'Post Normalized Score',
            'Post Title',
            'Post Content',
            'Post Content Length',
            'Post Revised Title',
            'Post Revised Content',
            'Post Revised Content Length',
            'Post Character',
            'Post Link',
            'Video ID'
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

        # Access the specified Google Sheet and worksheet
        self.sheet = client.open(sheet_name)
        try:
            self.worksheet = self.sheet.worksheet(worksheet_name)
        except gspread.exceptions.WorksheetNotFound:
            # Create the worksheet if it doesn't exist
            self.worksheet = self.sheet.add_worksheet(title=worksheet_name, rows=100, cols=20)
            self.initialize_sheet()


    def clear(self):
        """
        Clear the work sheet
        """
        self.worksheet.clear()


    def initialize_sheet(self):
        """
        Set up the sheet with headers if it is newly created.
        """
        headers = ["Priority", "Date Time", "Unique ID", "Post ID", "Post Revised Title", "Post Revised Content", "Post Character"]
        self.worksheet.append_row(headers)


    def push(self, post, priority=0):
        """
        Add a task to the priority queue with a precise timestamp.
        """
        # Prepare the new row
        date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")  # Include microseconds
        row = [priority, date_time, *(post.get(col) for col in self.headers[2:])]
        print("PQ UPDATED WITH row : ", row)
        self.worksheet.append_row(row)

        # Sort all data by priority (descending) and date time (ascending for ties)
        # Sorting logic is written in spread sheet AppScript



    def bulk_push(self, messages, priority=0):
        """
        Add multiple tasks to the priority queue with a precise timestamp and default priority value.
        """
        # Prepare new rows
        rows_to_insert = []
        for message in messages:
            date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")  # Include microseconds
            row = [priority, date_time, *(message.get(col) for col in self.headers[2:])]
            rows_to_insert.append(row)

        print("PQ UPDATED WITH rows_to_insert : ", rows_to_insert)
        self.worksheet.append_rows(rows_to_insert)
        # Sort all data by priority (descending) and date time (ascending for ties)
        # Sorting logic is written in spread sheet AppScript


    def is_empty(self):
        """
        checks if queue is empty
        """
        all_data = self.worksheet.get_all_values()

        # Skip header and check if there's any data
        if len(all_data) <= 1:
            print("No data available in the queue.")
            return True
        
        return False


    def front(self):
        """
        Return the highest priority task without removing it.
        """
        all_data = self.worksheet.get_all_values()

        # Skip header and check if there's any data
        if len(all_data) <= 1:
            print("No data available in the queue.")
            return None

        # Return the first row (highest priority task)
        print(f"Front task: {all_data[0]}")
        return {key: value for key, value in zip(all_data[0], all_data[1])}


    def pop(self):
        """
        Remove and return the highest priority task.
        """
        all_data = self.worksheet.get_all_values()

        # Skip header and check if there's any data
        if len(all_data) <= 1:
            print("No data available in the queue.")
            return None

        # Get the highest priority task (first row after header)
        task = {key: value for key, value in zip(all_data[0], all_data[1])}
        self.worksheet.delete_rows(2)
        print(f"Popped task: {task}")
        return task
