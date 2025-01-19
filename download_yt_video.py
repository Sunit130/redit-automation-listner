import os
import ffmpeg
import random
import multiprocessing
from yt_dlp import YoutubeDL
from mutagen.mp3 import MP3



class YoutubeDownload:

    def __init__(self):
        pass
    
    def cleanup_files():
        # List of files to check and remove
        files_to_remove = ["cliped_video.mp4"]

        print("\nStarted removeing used files from YT_DLP")
        for file in files_to_remove:
            if os.path.exists(file):
                try:
                    os.remove(file)
                    print(f"Removed: {file}")
                except Exception as e:
                    print(f"Error removing {file}: {e}")
            else:
                print(f"{file} does not exist.")


    @staticmethod
    def get_yt_dlp_options(start_time, end_time, cliped_file_path):
        # Inline function for 'download_ranges'
        download_ranges_callback_func = lambda info_dict, ydl: [
            {
                "start_time": start_time,
                "end_time": end_time,
                "title": f"Clip_{start_time}_{end_time}",  # Optional title based on range
            }
        ]

        options = {
            "format": "bestvideo",
            "cookiefile": "cookies.txt",
            "outtmpl": cliped_file_path,
            "download_ranges": download_ranges_callback_func,
            "overwrites": True,
        }
        return options

    @staticmethod
    def get_audio_length(file_path):
        """
        TODO: move to utils
        Get the length of an MP3 audio file in seconds using mutagen.

        :param file_path: Path to the audio file.
        :return: Length of the audio in seconds.
        """
        audio = MP3(file_path)
        return round(audio.info.length + 1)
    
    @staticmethod
    def get_video_duration(url):
        """
        Fetch the duration of the YouTube video.
        
        Args:
            url (str): The URL of the YouTube video.
        
        Returns:
            int: Duration of the video in seconds, or None if not found.
        """
        try:
            options = {
                "quiet": True,  # Suppress output for cleaner logs
                "no_warnings": True,
            }
            with YoutubeDL(options) as ydl:
                video_info = ydl.extract_info(url, download=False)
                return video_info.get("duration", None)  # Duration is in seconds
        except Exception as e:
            print(f"Error fetching video duration: {e}")
            return None


    def stream_and_crop_video(self, url, output_file_path, audio_path, subtitles_file, title_end_time, redit_id):

        audio_length = self.get_audio_length(audio_path)
        video_duration = self.get_video_duration(url)  
        start_time = random.randint(10, video_duration - audio_length)
        end_time = start_time + audio_length
        print("start_time : ", start_time, " | end_time : ", end_time, " | audio_length : ", audio_length , " | video_duration : ", video_duration)
        
        cliped_file_path = 'cliped_video.mp4'
        options = self.get_yt_dlp_options(start_time, end_time, cliped_file_path)

        with YoutubeDL(options) as ydl:
            # Extract video information
            video_info = ydl.extract_info(url, download=False)
            
            # Get the list of formats
            formats = video_info.get("formats", [])
            
            # Find the best format with resolution >= 1920x1080
            best_format = None
            for fmt in formats:
                if fmt.get("format_note", "") == '1080p60' and fmt.get("ext", "") == "mp4":
                    best_format = fmt
                    break

            if best_format:
                print(f"Selected Format: {best_format['format_id']} ({best_format['resolution']})")
                options["format"] = best_format["format_id"]
                with YoutubeDL(options) as downloader:
                    downloader.download([url])
            else:
                print("No format with 1920x1080 or higher resolution found.")

        audio_input = ffmpeg.input(audio_path)

        # Load the thumbnail
        thumbnail_input = ffmpeg.input(f"assets/temp/{redit_id}/png/title.png").filter("scale", 1000, -1)

        # First, load the background video
        background_clip = ffmpeg.input(cliped_file_path)

        # Add the subtitles first
        style = "FontName=Londrina Solid,FontSize=18,PrimaryColour=&H00ffffff,OutlineColour=&H00000000,BackColour=&H80000000,Bold=1,Italic=0,Alignment=10"
        background_clip_with_subtitles = background_clip.filter('subtitles', subtitles_file, force_style=style)

        # Then apply the overlay after the subtitles are added
        background_clip_with_overlay = background_clip_with_subtitles.overlay(
            thumbnail_input,
            enable=f"between(t,0,{title_end_time})",  # Adjust start and end time for the overlay
            x="(main_w-overlay_w)/2",  # Center horizontally
            y="(main_h-overlay_h)/2"   # Center vertically
        )

        print("Scaling video to requested height and width")
        (
            background_clip_with_overlay  # The background video with subtitles and overlay
            .output(
                audio_input,  # The audio input
                output_file_path,  # Output file path
                **{
                    "c:v": "h264",  # Video codec
                    "b:v": "20M",  # Video bitrate
                    "b:a": "192k",  # Audio bitrate
                    "shortest": None,  # Stop when the shortest stream ends
                }
            )
            .run(overwrite_output=True)
        )










        # Prepare yt-dlp options to fetch the video stream
        # ydl_opts = {
        #     'format': 299,
        #     'noplaylist': True,     # Avoid downloading playlists
        #     'quiet': True,          # Reduce verbosity
        #     'outtmpl': '-',         # Output to stdout (pipe it to ffmpeg)
        #     'cookiefile': 'cookies.txt'
        # }

        # # Use yt-dlp to get the video stream
        # with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        #     info_dict = ydl.extract_info(url, download=False)

        #     video_url = None
        #     video_format_info = None
        #     print("info_dict['formats'] : ", info_dict['formats'])
        #     for format_info in info_dict['formats']: 
        #         if format_info["resolution"] and 'x' in format_info["resolution"]:
        #             w, h = format_info["resolution"].split('x')
        #             print("resolution : ", format_info["resolution"])
        #             if int(h) == 1080 and format_info["video_ext"] == 'mp4':  # TODO: LOOK FOR BETTER WAYS TO FILTER
        #                 video_url = format_info['url']
        #                 video_format_info = format_info 
        #                 break
        #     print("video_format_info : ",video_format_info)
        #     if not video_url:
        #         raise ValueError("No MP4 format found for the video.")
            
        #     # Pipe the video URL to ffmpeg, crop, and save it locally
        #     video_input = ffmpeg.input(video_url, ss=start_time, t=end_time - start_time)

        #     cropped_output_file = 'cropped_output_file.mp4'
        #     cropped_video_output = (
        #         ffmpeg
        #         .output(video_input, cropped_output_file, vcodec='libx264', movflags='+faststart', preset='ultrafast')
        #         .run(overwrite_output=True)
        #     )

        #     cropped_video_input = ffmpeg.input(cropped_output_file)
        #     audio_input = ffmpeg.input(audio_file)

        #     # Apply crop and subtitles as part of the filtergraph
        #     video_with_subtitles = cropped_video_input.filter('crop', w='ih*9/16', h='ih', x='(iw-ih*9/16)/2', y=0).filter('subtitles', subtitles_file)
            
        #     # Combine video and audio streams
        #     (
        #         ffmpeg
        #         .output(video_with_subtitles, audio_input, output_file_path,
        #                 vcodec='libx264',
        #                 acodec='aac',
        #                 movflags='+faststart',
        #                 preset='ultrafast',
        #                 shortest=None)
        #         .run(overwrite_output=True)
        #     )




# # # Example usage
# url = 'https://www.youtube.com/watch?v=n_Dv4JMiwK8'  # Replace with your video URL
# start_time = 30  # Start time in seconds
# end_time = 60    # End time in seconds
# output_file = 'output_video2.mp4'  # Output file name
# audio_file = 'results/diuucz/audio.mp3'
# subtitles_file = 'results/diuucz/subtitles.srt'

# YoutubeDownload().stream_and_crop_video(url, start_time, end_time, output_file, audio_file, subtitles_file)
