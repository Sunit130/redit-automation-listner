import os
import yt_dlp
import ffmpeg


class YoutubeDownload:

    def __init__(self):
        pass
    
    def cleanup_files():
        # List of files to check and remove
        files_to_remove = ["cropped_output_file.mp4"]

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

    def stream_and_crop_video(self, url, start_time, end_time, output_file_path, audio_file, subtitles_file):
        # Prepare yt-dlp options to fetch the video stream
        ydl_opts = {
            'noplaylist': True,     # Avoid downloading playlists
            'quiet': True,          # Reduce verbosity
            'outtmpl': '-',         # Output to stdout (pipe it to ffmpeg)
            'cookiefile': 'cookies.txt'
        }

        # Use yt-dlp to get the video stream
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)

            video_url = None
            for format_info in info_dict['formats']:
                if format_info['video_ext'] == 'mp4' and format_info["height"] == 1080:  # TODO: LOOK FOR BETTER WAYS TO FILTER
                    video_url = format_info['url']
                    break
            
            if not video_url:
                raise ValueError("No MP4 format found for the video.")
            
            # Pipe the video URL to ffmpeg, crop, and save it locally
            video_input = ffmpeg.input(video_url, ss=start_time, t=end_time - start_time)

            cropped_output_file = 'cropped_output_file.mp4'
            cropped_video_output = (
                ffmpeg
                .output(video_input, cropped_output_file, vcodec='libx264', movflags='+faststart', preset='ultrafast')
                .run(overwrite_output=True)
            )

            cropped_video_input = ffmpeg.input(cropped_output_file)
            audio_input = ffmpeg.input(audio_file)

            # Apply crop and subtitles as part of the filtergraph
            video_with_subtitles = cropped_video_input.filter('crop', w='ih*9/16', h='ih', x='(iw-ih*9/16)/2', y=0).filter('subtitles', subtitles_file)
            
            # Combine video and audio streams
            (
                ffmpeg
                .output(video_with_subtitles, audio_input, output_file_path,
                        vcodec='libx264',
                        acodec='aac',
                        movflags='+faststart',
                        preset='ultrafast',
                        shortest=None)
                .run(overwrite_output=True)
            )




# # # Example usage
# url = 'https://www.youtube.com/watch?v=n_Dv4JMiwK8'  # Replace with your video URL
# start_time = 30  # Start time in seconds
# end_time = 60    # End time in seconds
# output_file = 'output_video2.mp4'  # Output file name
# audio_file = 'results/diuucz/audio.mp3'
# subtitles_file = 'results/diuucz/subtitles.srt'

# YoutubeDownload().stream_and_crop_video(url, start_time, end_time, output_file, audio_file, subtitles_file)
