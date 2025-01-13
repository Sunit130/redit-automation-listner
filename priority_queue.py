import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import uuid
import json
import os
from utils import get_google_service_account_key

class PriorityQueue:
    def __init__(self, sheet_name, worksheet_name="Queue"):
        # Authenticate and initialize the Google Sheet
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]
        service_account_key = os.environ.get("SERVICE_ACCOUNT_KEY")

        if not service_account_key:
            raise ValueError("SERVICE_ACCOUNT_KEY environment variable is not set or is empty")

        try:
            print("service_account_key : ", service_account_key)
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


    def push(self, post_id, title, content, character, priority=0):
        """
        Add a task to the priority queue with a precise timestamp.
        """
        # Get all the existing data from the worksheet
        all_data = self.worksheet.get_all_values()
        
        # Prepare the new row
        date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")  # Include microseconds
        unique_id = str(uuid.uuid4())  # Generate a unique identifier
        row = [priority, date_time, unique_id, post_id, title, content, character]
        
        # Append the new rows to the existing data (skipping header)
        data = all_data[1:]  # Get all the data, skipping the header
        data.extend([row])  # Add new rows to the data list

        # Sort all data by priority (descending) and date time (ascending for ties)
        sorted_data = sorted(data, key=lambda x: (-int(x[0]), x[1]))  # Sort only the data

        # Clear the worksheet and append the header and sorted data in one go
        self.worksheet.clear()
        self.worksheet.append_row(all_data[0])  # Append header row
        self.worksheet.append_rows(sorted_data)  # Append sorted data



    def bulk_push(self, messages, priority=0):
        """
        Add multiple tasks to the priority queue with a precise timestamp and default priority value.
        """
        # Get all the existing data from the worksheet
        all_data = self.worksheet.get_all_values()

        # Prepare new rows
        rows_to_insert = []
        for message in messages:
            date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")  # Include microseconds
            unique_id = str(uuid.uuid4())  # Generate a unique identifier
            row = [priority, date_time, unique_id, message['Post ID'], message['Post Revised Title'], message['Post Revised Content'], message['Post Character']]
            rows_to_insert.append(row)

        print("rows_to_insert : ", rows_to_insert)
        
        # Append the new rows to the existing data (skipping header)
        data = all_data[1:]  # Get all the data, skipping the header
        data.extend(rows_to_insert)  # Add new rows to the data list
        print("data after extending : ", data)

        # Sort all data by priority (descending) and date time (ascending for ties)
        sorted_data = sorted(data, key=lambda x: (-int(x[0]), x[1]))  # Sort only the data
        print("sorted_data : ", sorted_data)

        # Clear the worksheet and append the header and sorted data in one go
        self.worksheet.clear()
        self.worksheet.append_row(all_data[0])  # Append header row
        self.worksheet.append_rows(sorted_data)  # Append sorted data


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


# Example Usage
# if __name__ == "__main__":
#     pq = PriorityQueue(sheet_name="Redit Posts")

#     # List of messages to push in bulk
#     messages = [
#         {
#             'Post ID': 'Post123',
#             'Post Revised Title': 'Title A',
#             'Post Revised Content': 'Content A',
#             'Post Character': 'Character A',
#         },
#         {
#             'Post ID': 'Post456',
#             'Post Revised Title': 'Title B',
#             'Post Revised Content': 'Content B',
#             'Post Character': 'Character B',
#         },
#         {
#             'Post ID': 'Post452',
#             'Post Revised Title': 'Title a',
#             'Post Revised Content': 'Contant B',
#             'Post Character': 'Character a',
#         },
#         {
#             'Post ID': 'Post451',
#             'Post Revised Title': 'Title d',
#             'Post Revised Content': 'Content B',
#             'Post Character': 'Character d',
#         }
#     ]
    
#     # Push multiple messages in bulk
#     # pq.bulk_push(messages)

#     pq.push(
#     post_id=1,
#     title="asdasdasdasd",
#     content="asdasdasdasd",
#     character="asdasdasdasd",
#     priority=1)

#     pq.pop()

#     # View the updated queue
#     print("Queue after bulk push:", pq.worksheet.get_all_values())
