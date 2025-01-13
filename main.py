
import asyncio
import edge_tts
import sys
import os
import time
import random


from mutagen.mp3 import MP3
from moviepy  import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip

from google_drive import GoogleDrive
from download_yt_video import YoutubeDownload
from priority_queue import PriorityQueue



async def text_to_speech(text, voice, audio_path, subtitles_path):

    print("Started for : ", voice )
    communicate = edge_tts.Communicate(text, voice, rate="+10%")
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


def get_audio_length(file_path):
    """
    Get the length of an MP3 audio file in seconds using mutagen.

    :param file_path: Path to the audio file.
    :return: Length of the audio in seconds.
    """
    audio = MP3(file_path)
    return round(audio.info.length + 1)



def time_to_seconds(timestamp):
    hours, minutes, seconds = timestamp.split(':')
    seconds, milliseconds = seconds.split(',')
    total_seconds = int(hours) * 3600 + int(minutes) * 60 + int(seconds) + int(milliseconds) / 1000.0
    return total_seconds


def add_audio_and_subtitles_to_video(video_path, audio_path, subtitles_path, output_video_path):
    # Load video
    video = VideoFileClip(video_path, audio=False)

    # Load audio
    audio = AudioFileClip(audio_path)

    # Set audio to video
    video = video.with_audio(audio)

    # Create a subtitles overlay using the SRT file
    # Generate subtitle clips based on the SRT file
    subtitle_clips = []
    last_end_time = 0  # Store the last subtitle's end time
    with open(subtitles_path, 'r') as file:
        srt_lines = file.readlines()

    i = 0
    while i < len(srt_lines):
        if '-->' in srt_lines[i]:
            start_time, end_time = srt_lines[i].split(' --> ')
            start_time = time_to_seconds(start_time.strip())
            end_time = time_to_seconds(end_time.strip())
            subtitle_text = srt_lines[i + 1].strip()  # Get the subtitle text from next line
            
            # Create a TextClip for the subtitle
            subtitle = (TextClip(text=subtitle_text, color='white', font_size=54, interline=7, bg_color='black', font="Lato-Regular.ttf", duration=float(end_time) - float(start_time))
                        .with_position(("center","center"))
                        .with_start(float(start_time)))
            subtitle_clips.append(subtitle)
            last_end_time = float(end_time)
            i += 2  # Move to the next subtitle
        else:
            i += 1

    video = video.subclipped(0, last_end_time)


    # Combine the subtitle clips
    final_video = CompositeVideoClip([video] + subtitle_clips)
    print("File composition done : writing it now")
    # Write the final video with audio and subtitles
    final_video.write_videofile(output_video_path, codec="libx264", audio_codec="aac")


def cleanup_files():
    # List of files to check and remove
    files_to_remove = ["audio.mp3", "subtitles.srt", "result.mp4", "cropped_output_file.mp4"]

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


def list_files_in_current_directory():
    # Get a list of all files and directories in the current directory
    files = os.listdir(".")
    print("\nFiles and directories in the current directory:")
    for file in files:
        print(file)


def process(args):

    try:

        print("STARTED FETCHING POST FROM PQ")
        start = time.time()
        pq = PriorityQueue(sheet_name="Redit Posts")
        post = pq.front()
        end = time.time()
        print("GOT THE POST FROM QUEUE")
        print(f"Time taken: {end - start:.2f} seconds\n")


        print("STARTED FETCHING POST FROM PQ")
        start = time.time()
        pq = PriorityQueue(sheet_name="Redit Posts")
        post = pq.front()
        end = time.time()
        print("GOT THE POST FROM QUEUE")
        print(f"Time taken: {end - start:.2f} seconds\n")


        print("STARTED DOWNLOADING BACKGROUND VIDEO")
        start = time.time()
        url = 'https://www.youtube.com/watch?v=n_Dv4JMiwK8'  # Replace with your video URL
        start_time = 30  # Start time in seconds
        end_time = 60    # End time in seconds
        output_file = 'result.mp4'  # Output file name
        audio_file = 'results/diuucz/audio.mp3'
        subtitles_file = 'results/diuucz/subtitles.srt'
        YoutubeDownload().stream_and_crop_video(url, start_time, end_time, output_file, audio_file, subtitles_file)
        end = time.time()
        print("COMPLETED DOWNLOADING BACKGROUND VIDEO")
        print(f"Time taken: {end - start:.2f} seconds\n")

        print("STARTED GOOGLE DRIVE UPLOADING")
        start = time.time()
        child_folder_name = 'diuucz'
        parent_folder_id = "1PVR606GT6kWsuqGt97mH4NEv3SmvJww5"

        drive = GoogleDrive()
        output_video_path = f'result.mp4'
        drive_service = drive.authenticate_with_service_account()
        child_folder_id = drive.create_folder(drive_service, child_folder_name, parent_folder_id)
        drive.upload_video_to_drive(drive_service, output_video_path, child_folder_id)
        end = time.time()
        print("COMPLETED GOOGLE DRIVE UPLOADING")
        print(f"Time taken: {end - start:.2f} seconds\n")


        # claenup 
        print("STARTED CLEANUPs")
        start = time.time()
        list_files_in_current_directory()
        cleanup_files()
        list_files_in_current_directory()
        end = time.time()
        print("COMPLETED CLEANUP")
        print(f"Time taken: {end - start:.2f} seconds\n")
    except Exception as e:
        print("CAUGHT EXCEPTION : ", str(e))
        print("STARTED CLEANUPs")
        start = time.time()
        list_files_in_current_directory()
        cleanup_files()
        list_files_in_current_directory()
        end = time.time()
        print("COMPLETED CLEANUP")
        print(f"Time taken: {end - start:.2f} seconds\n")
    return
    voices = {
        "male": "en-US-AndrewNeural",
        "female": "en-US-AvaNeural"
    }
    cleanup_files()
    overall_start = time.time()  # Start overall timing

    print("STARTED FETCHING POST FROM PQ")
    start = time.time()
    pq = PriorityQueue(sheet_name="Redit Posts")
    post = pq.front()
    end = time.time()
    print("GOT THE POST FROM QUEUE")
    print(f"Time taken: {end - start:.2f} seconds\n")

    print("STARTED TEXT TO SPEECH PROCESS")
    start = time.time()
    script = f'{post["Post Revised Title"]} \n\n {post["Post Revised Content"]}'
    voice = voices.get(post["Post Character"], "male")
    folder_path = f'results/{post["Post ID"]}'
    # create_folder_if_not_exists(folder_path)
    audio_path = f'audio.mp3'
    subtitles_path = f'subtitles.srt'
    asyncio.run(text_to_speech(script, voice, audio_path, subtitles_path))
    end = time.time()
    print("COMPLETED TEXT TO SPEECH PROCESS")
    print(f"Time taken: {end - start:.2f} seconds\n")

    print("STARTED DOWNLOADING BACKGROUND VIDEO")
    start = time.time()
    minecraft_video_url = 'https://www.youtube.com/watch?v=n_Dv4JMiwK8'
    bg_video_length = 4813  # TODO : get this from yt-dlp itself in info
    audio_length = get_audio_length(audio_path)

    # # Make this randomize
    start_time = random.randint(10, bg_video_length - audio_length)
    end_time = start_time + audio_length
    print("start_time : ", start_time, " | end_time : ", end_time)
    output_video_path = f'result.mp4'
    # TODO: try to add multi-resolution option
    YoutubeDownload().stream_and_crop_video(url=minecraft_video_url, start_time=start_time, end_time=end_time, output_file_path=output_video_path, audio_file=audio_path, subtitles_file=subtitles_path)
    end = time.time()
    print("BACKGROUND VIDEO DOWNLOAD COMPLETE")
    print(f"Time taken: {end - start:.2f} seconds\n")


    # print("STARTED STITCHING BG + AUDIO + SUBS")
    # start = time.time()
    # output_video_path = f'{folder_path}/result.mp4'
    # add_audio_and_subtitles_to_video(background_video_path, audio_path, subtitles_path, output_video_path)
    # end = time.time()
    # print("COMPLETED STITCHING BG + AUDIO + SUBS")
    # print(f"Time taken: {end - start:.2f} seconds\n")


    print("STARTED GOOGLE DRIVE UPLOADING")
    start = time.time()
    child_folder_name = post["Post ID"]
    parent_folder_id = "1PVR606GT6kWsuqGt97mH4NEv3SmvJww5"

    drive = GoogleDrive()

    drive_service = drive.authenticate_with_service_account()
    child_folder_id = drive.create_folder(drive_service, child_folder_name, parent_folder_id)
    drive.upload_video_to_drive(drive_service, output_video_path, child_folder_id)
    end = time.time()
    print("COMPLETED GOOGLE DRIVE UPLOADING")
    print(f"Time taken: {end - start:.2f} seconds\n")



    # claenup 
    print("STARTED CLEANUP")
    start = time.time()
    list_files_in_current_directory()
    cleanup_files()
    list_files_in_current_directory()
    end = time.time()
    print("COMPLETED CLEANUP")
    print(f"Time taken: {end - start:.2f} seconds\n")


    overall_end = time.time()
    print(f"Overall time taken: {overall_end - overall_start:.2f} seconds")
    # srt_to_ass_with_styles("results/diuucz/subtitles.srt", "results/diuucz/subtitles.ass")








if __name__ == '__main__':
    process(None)

#     result_path = 'results'
#     video_id = 'xuawe'

#     start_time = 30  # Start time in seconds
#     end_time = 90    # End time in seconds
#     video_file_path = f'{result_path}/output_video2.mp4'  # Output file name
#     url = 'https://www.youtube.com/watch?v=n_Dv4JMiwK8'
#     YoutubeDownload().stream_and_crop_video(url, start_time, end_time, video_file_path)


#     child_folder_name = video_id
#     parent_folder_id = "1PVR606GT6kWsuqGt97mH4NEv3SmvJww5"

#     drive = GoogleDrive()

#     drive_service = drive.authenticate_with_service_account()
#     child_folder_id = drive.create_folder(drive_service, child_folder_name, parent_folder_id)
#     drive.upload_video_to_drive(drive_service, video_file_path, child_folder_id)
