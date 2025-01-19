from datetime import datetime
import os
import gspread
import json
from priority_queue import PriorityQueue
from oauth2client.service_account import ServiceAccountCredentials


class PostsSpreadSheet:
    
    def __init__(self, sheet_name, worksheet_name="Content Ready"):
        # Authenticate and initialize the Google Sheet
        service_account_key = os.environ.get("SERVICE_ACCOUNT_KEY")
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]
        self.headers = [
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
            'Video ID',
            'Upload Time'
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
        self.worksheet = self.sheet.worksheet(worksheet_name)


    def initialize_google_sheet(self):
        self.worksheet.clear()
        self.worksheet.append_row(self.headers)


    # Function to add posts to Google Sheets
    def add_to_google_sheets(self, posts):
        all_rows = self.worksheet.get_all_records()
        already_available_post_ids = [row['Post ID'] for row in all_rows]
        # Add data rows
        data = [
            [
                post['id'],
                post['post_date'],
                post['post_subreddit'],
                post['progress'],
                post['score'],
                post['normalized_score'],
                post['title'],
                post['content'],
                post['content_length'],
                post['revised_title'],
                post['revised_content'],
                post['revised_content_length'],
                post['character'],
                post['post_link'],
                None
            ]
            for post in posts if post['id'] not in already_available_post_ids
        ]
        if not data:
            raise "Posts already available or no new posts on redit"
        self.worksheet.insert_rows(data, 2)


    def populate_queue_messages(self):
        """Polulates the priority queue with messages for video processing."""
        all_rows = self.worksheet.get_all_records()
        print("got all posts")

        top_ready_posts = all_rows[:5]
        print("Get top 5 posts from Content Ready")

        for post in top_ready_posts:
            post['Post Progress'] = 'VIDEO_QUEUED'

        pq = PriorityQueue(sheet_name="Redit Posts")
        pq.bulk_push(top_ready_posts)

        print(f"Updated status UPDATED for redit-posts")


    def add_post_yt_unlisted_sheet(self, post, video_id, populate_sheet_name):
        """Updates the 'Video ID' column for a post with the given post_id."""
        polulated_worksheet = self.sheet.worksheet(populate_sheet_name)
        post['Video ID'] = video_id
        post['Post Progress'] = 'YT_UNLISTED'
        post['Upload Time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        entry = [ post.get(col) for col in self.headers]
        polulated_worksheet.append_row(entry)
        print(f"Updated Video ID for Post ID: {post['Post ID']}")



