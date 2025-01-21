
import asyncio
import edge_tts
import sys
import os
import time
import json
import random
import shutil
import re
from PIL import Image
from pathlib import Path
from download_yt_video import YoutubeDownload
from post_sheet import PostsSpreadSheet
from priority_queue import PriorityQueue
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload
from thumbnail import create_fancy_thumbnail, name_normalize
from googleapiclient.discovery import build
from utils import print_storage_info
from dotenv import load_dotenv
from const import MINECRAFT_VIDEO_LIST

load_dotenv()

SCOPES = {
    "drive": ["https://www.googleapis.com/auth/drive.readonly"],
    "youtube": ["https://www.googleapis.com/auth/youtube.upload"],
}

CONTENT_READY_WORKSHEET = "Content Ready"
PRIORITY_QUEUE_WORKSHEET = "Queue"
YOUTUBE_UNLISTED_WORKSHEET = "Youtube Unlisted"
YOUTUBE_PUBLIC_WORKSHEET = "Youtube Public"



async def text_to_speech(text, voice, pitch, audio_path, subtitles_path):

    print("\nStarted for : ", voice )
    communicate = edge_tts.Communicate(text, voice, rate="+15%", pitch=pitch)
    submaker = edge_tts.SubMaker()
    try:
        audio_file = (
            open(audio_path, "wb")
            if audio_path is not None and audio_path != "-"
            else sys.stdout.buffer
        )
        sub_file = (
            open(subtitles_path, "w", encoding="utf-8")
            if subtitles_path is not None and subtitles_path != "-"
            else None
        )
        if sub_file is None and subtitles_path == "-":
            sub_file = sys.stderr

        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_file.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                submaker.feed(chunk)

        if sub_file is not None:
            subtitles = submaker.get_srt()
            updated_subtitles = ""
            lines = subtitles.splitlines()

            # Add {\an5} from index 2 and then every 4th line
            for i in range(2, len(lines), 4):
                if "-->" not in lines[i]:  # Ignore time range lines
                    lines[i] = f"{{\\an5}}{lines[i]}"

            # Reconstruct the updated subtitle text
            updated_subtitles = "\n".join(lines)
            sub_file.write(updated_subtitles)
    finally:
        if audio_file is not sys.stdout.buffer:
            audio_file.close()
        if sub_file is not None and sub_file is not sys.stderr:
            sub_file.close()
    print("Completed for : ", voice )
    print(f"Audio saved to {audio_path}")
    print(f"Subtitles saved to {subtitles_path}")



# utils
def create_folder_if_not_exists(folder_path):
    """
    Create a folder if it doesn't exist.

    :param folder_path: Path to the folder to create.
    """
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Folder created: {folder_path}")
    else:
        print(f"Folder already exists: {folder_path}")


def time_to_seconds(timestamp):
    hours, minutes, seconds = timestamp.split(':')
    seconds, milliseconds = seconds.split(',')
    total_seconds = int(hours) * 3600 + int(minutes) * 60 + int(seconds) + int(milliseconds) / 1000.0
    return total_seconds


def cleanup_files():
    # List of files to check and remove
    files_to_remove = ["audio.mp3", "subtitles.srt", "result.mp4", "cliped_video.mp4"]

    print("\nStarted removeing used files")
    for file in files_to_remove:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"Removed: {file}")
            except Exception as e:
                print(f"Error removing {file}: {e}")
        else:
            print(f"{file} does not exist.")

    directory = f"assets/temp/"
    if os.path.exists(directory):
        shutil.rmtree(directory)


def list_files_in_current_directory():
    # Get a list of all files and directories in the current directory
    files = os.listdir(".")
    print("\nFiles and directories in the current directory:")
    for file in files:
        print(file)


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
    return creds


def upload_video_to_youtube(video_file, title, description, category, youtube_service):
    # Prepare the request body for uploading the video
    request_body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": [category, f'{category} stories', "redit stories", "minecraft parkor"],
        },
        "status": {
            "privacyStatus": "unlisted",
            "embeddable": True,
            "selfDeclaredMadeForKids": False
        },
    }

    # Upload the video
    media = MediaFileUpload(video_file, chunksize=-1, resumable=True)
    request = youtube_service.videos().insert(
        part="snippet,status", body=request_body, media_body=media
    )
    response = request.execute()
    yt_video_id = response.get('id')
    print(f"Uploaded video ID: {response.get('id')}")
    return yt_video_id


def find_title_end_time_by_words(srt_file_path, title):
    # Open and read the SRT file
    print("SUB: ", srt_file_path, " | title : ", title)
    with open(srt_file_path, "r") as file:
        subtitles = file.read()

    # Split the title into individual words
    title_words = title.split()
    title_index = 0  # Track which word in the title we're matching

    # Split into individual blocks
    blocks = subtitles.strip().split("\n\n")
    for block in blocks:
        # Extract time and subtitle text using regex
        match = re.search(r"(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.+)", block, re.DOTALL)
        if match:
            start_time, end_time, text = match.groups()
            # Remove formatting (like {\an5}) and strip the text
            cleaned_text = re.sub(r"{\\an\d+}", "", text).strip()
            print(f"Checking block: {block}")
            print(f"Cleaned Text: '{cleaned_text}', Title Word: '{title_words[title_index]}'")
            # Check if the current subtitle matches the current title word
            if cleaned_text == title_words[title_index]:
                title_index += 1  # Move to the next word in the title
                print(f"Matched word '{cleaned_text}' at index {title_index}")
                # If we've matched all words in the title, return the end time
                if title_index == len(title_words):
                    print(f"Title end time found: {end_time}")

                    return time_to_seconds(end_time)

    print("Title not found in subtitles.")
    return None



def process(args):

    try:
        voices = {
            "male": {'voice': "en-US-AndrewNeural", 'pitch': '+0Hz'},
            "female": {'voice': "en-US-AvaNeural", 'pitch': '-10Hz'}
        }
        audio_path = f'audio.mp3'
        subtitles_path = f'subtitles.srt'
        overall_start = time.time()  # Start overall timing

        redit_post_sheet = PostsSpreadSheet(sheet_name="Redit Posts")
        priority_queue_sheet = PriorityQueue(sheet_name="Redit Posts")

        print("CHECKS IF PRIORITY QUEUE IS EMPTY")
        if priority_queue_sheet.is_empty():
            print("FOUND PRIORITY QUEUE IS EMPTY")
            redit_post_sheet.populate_queue_messages()
            time.sleep(1)

        print("\nSTARTED FETCHING POST FROM priority_queue_sheet")
        start = time.time()
        post = priority_queue_sheet.front()
        end = time.time()
        print("GOT THE POST FROM QUEUE")
        print(f"Time taken: {end - start:.2f} seconds\n")
    
        redit_post_id = post["Post ID"]
        script_title = post["Post Revised Title"]
        script_content = post["Post Revised Content"]
        category = post["Post Sub-Reddit"]

        print("\nSTARTED TEXT TO SPEECH PROCESS")
        start = time.time()
        script = f'{script_title} \n\n {script_content}'
        voice = voices.get(post["Post Character"], "male")
        asyncio.run(text_to_speech(script, voice['voice'], voice['pitch'], audio_path, subtitles_path))
        end = time.time()
        print("COMPLETED TEXT TO SPEECH PROCESS")
        print(f"Time taken: {end - start:.2f} seconds\n")

        
        print("\nSTARTED PREPRAING THE THUMBNAIL")
        start = time.time()
        title_template = Image.open("assets/title_template.png")
        normalize_script_title = name_normalize(script_title)
        font_color = "#000000"
        padding = 5
        Path(f"assets/temp/{redit_post_id}/png").mkdir(parents=True, exist_ok=True)
        title_img = create_fancy_thumbnail(title_template, script_title, font_color, padding)
        title_img.save(f"assets/temp/{redit_post_id}/png/title.png")
        title_end_time = find_title_end_time_by_words(subtitles_path, normalize_script_title)
        end = time.time()
        print("title_end_time : ", title_end_time)
        print("COMPLETED PREPRAING THE THUMBNAIL")
        print(f"Time taken: {end - start:.2f} seconds\n")
    

        print("\nSTARTED DOWNLOADING BACKGROUND VIDEO")
        start = time.time()
        audio_length = YoutubeDownload.get_audio_length(audio_path)
        filtered_videos = list(filter(lambda x: x["duration"] > audio_length, MINECRAFT_VIDEO_LIST))
        selected_video = filtered_videos[random.randint(0, len(filtered_videos)-1)]
        bg_video_url = selected_video["url"]
        video_duration = selected_video["duration"]
        print("before - audio.mp3 audio_length : ", audio_length, " | \nfiltered_videos : ", filtered_videos, "\n")
        output_video_path = f'result.mp4'
        YoutubeDownload().stream_and_crop_video(
            url = bg_video_url, 
            output_file_path = output_video_path, 
            audio_path = audio_path, 
            subtitles_file = subtitles_path,
            title_end_time = title_end_time,
            redit_id = redit_post_id,
            video_duration = video_duration
            )
        end = time.time()
        print("BACKGROUND VIDEO DOWNLOAD COMPLETE")
        print(f"Time taken: {end - start:.2f} seconds\n")
    
        print_storage_info()

        print("\nSTARTED YOUTUBE UPLOADING")
        start = time.time()
        youtube_credentials_json = os.getenv("YOUTUBE_CREDENTIALS")
        if not youtube_credentials_json:
            print("Missing Youtube environment variables for credentials.")
            raise "Error: Missing Youtube credentials."
        youtube_credentials_info = json.loads(youtube_credentials_json)
        youtube_creds = authenticate_with_user_info(SCOPES["youtube"], youtube_credentials_info)
        youtube_service = build("youtube", "v3", credentials=youtube_creds)
        video_title = script_title
        video_description = f'{category} story'
        video_id = upload_video_to_youtube(output_video_path, video_title, video_description, category, youtube_service)
        end = time.time()
        print("COMPLETED YOUTUBE UPLOADING")
        print(f"Time taken: {end - start:.2f} seconds\n")

        # Update the spreadsheet
        print("\nStarted updating youtube video file id in POSTS sheet")
        start = time.time()
        redit_post_sheet.add_post_yt_unlisted_sheet(post, video_id, YOUTUBE_UNLISTED_WORKSHEET)
        end = time.time()
        print("COMPLETED updating youtube video file id in POSTS sheet")
        print(f"Time taken: {end - start:.2f} seconds\n")

        # Remove processed request
        print("\nStarted removing processed request from queue")
        start = time.time()
        priority_queue_sheet.pop()
        end = time.time()
        print("Completed Removing processed request from queue")
        print(f"Time taken: {end - start:.2f} seconds\n")
    
        overall_end = time.time()
        print(f"Overall time taken: {overall_end - overall_start:.2f} seconds")
    finally:
        print("\nSTARTED CLEANUPs")
        print_storage_info()
        start = time.time()
        list_files_in_current_directory()
        cleanup_files()
        file = 'cookies.txt'
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"Removed: {file}")
            except Exception as e:
                print(f"Error removing {file}: {e}")
        else:
            print(f"{file} does not exist.")
        list_files_in_current_directory()
        end = time.time()
        print_storage_info()
        print("COMPLETED CLEANUP")
        print(f"Time taken: {end - start:.2f} seconds\n")


if __name__ == '__main__':
    process(None)


