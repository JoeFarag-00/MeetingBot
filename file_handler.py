import os
import logging
import config

class FileHandler:
    """Handles file system operations like directory creation, file listing, and saving outputs."""

    def __init__(self):
        self.video_dir = config.VIDEO_DIR
        self.transcript_dir = config.TRANSCRIPT_DIR
        self.summary_dir = config.SUMMARY_DIR
        self.audio_temp_dir = config.AUDIO_TEMP_DIR
        self.supported_extensions = config.SUPPORTED_VIDEO_EXTENSIONS

    def create_directories(self):
        """Creates necessary output directories if they don't exist."""
        os.makedirs(self.video_dir, exist_ok=True)
        os.makedirs(self.transcript_dir, exist_ok=True)
        os.makedirs(self.summary_dir, exist_ok=True)
        os.makedirs(self.audio_temp_dir, exist_ok=True)
        print(f"Ensured directories exist: {self.video_dir}, {self.transcript_dir}, {self.summary_dir}, {self.audio_temp_dir}")

    def get_video_files(self) -> list[str]:
        """Lists video files in the configured video directory."""
        try:
            files = [
                f for f in os.listdir(self.video_dir)
                if os.path.isfile(os.path.join(self.video_dir, f))
                and f.lower().endswith(self.supported_extensions)
            ]
            if not files:
                print(f"No video files with supported extensions ({', '.join(self.supported_extensions)}) found in {self.video_dir}.")
            else:
                print(f"Found {len(files)} video file(s) in {self.video_dir}.")
            return files
        except FileNotFoundError:
            print(f"Error: Video directory not found: {self.video_dir}")
            return []
        except Exception as e:
            print(f"Error listing video files in {self.video_dir}: {e}")
            return []

    def get_paths(self, video_file: str) -> tuple[str, str, str, str]:
        """Generates the full paths for video, audio, transcript, and summary files."""
        base_name = os.path.splitext(video_file)[0]
        video_path = os.path.join(self.video_dir, video_file)
        audio_path = os.path.join(self.audio_temp_dir, f"{base_name}.mp3")
        transcript_path = os.path.join(self.transcript_dir, f"{base_name}.txt")
        summary_path = os.path.join(self.summary_dir, f"{base_name}_summary.txt")
        return video_path, audio_path, transcript_path, summary_path

    def save_text(self, text: str, file_path: str):
        """Saves the given text to the specified file path."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"Output saved to {file_path}")
        except IOError as e:
            print(f"Error saving file to {file_path}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred while saving {file_path}: {e}")


    def cleanup_temp_audio(self, audio_path: str):
        """Removes the temporary audio file."""
        try:
            if os.path.exists(audio_path):
                os.remove(audio_path)
                print(f"Cleaned up temporary audio: {audio_path}")
            else:
                print(f"Temporary audio file not found, skipping cleanup: {audio_path}")
        except OSError as e:
            print(f"Error removing temporary audio file {audio_path}: {e}")
        except Exception as e:
            print(f"An unexpected error occurred during cleanup of {audio_path}: {e}") 