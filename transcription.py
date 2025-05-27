import os
import logging
import ffmpeg
from faster_whisper import WhisperModel
import config

# Configure logging for faster_whisper
logging.basicConfig()
logging.getLogger("faster_whisper").setLevel(logging.INFO) # Adjust level as needed (e.g., logging.WARNING)

class Transcriber:
    """Handles audio extraction and transcription using Faster Whisper."""

    def __init__(self):
        self.model_size = config.MODEL_SIZE
        self.device = config.DEVICE
        self.compute_type = config.COMPUTE_TYPE
        self.model = self._initialize_model()

    def _initialize_model(self):
        """Initializes the faster-whisper model."""
        print(f"Initializing faster-whisper model ({self.model_size}, {self.device}, {self.compute_type})...")
        try:
            model = WhisperModel(self.model_size, device=self.device, compute_type=self.compute_type)
            print("Faster-whisper model initialized successfully.")
            return model
        except Exception as e:
            print(f"Error initializing faster-whisper model: {e}")
            print("Please check your faster-whisper/CTranslate2 setup, CUDA compatibility (if using GPU), and model availability.")
            return None

    def extract_audio(self, video_path: str, audio_path: str) -> str | None:
        """Extracts audio from video file using ffmpeg-python and saves it.

        Args:
            video_path: Path to the input video file.
            audio_path: Path to save the extracted audio file.

        Returns:
            Path to the extracted audio file, or None if extraction failed.
        """
        if not os.path.exists(video_path):
            print(f"Error: Video file not found at {video_path}")
            return None

        print(f"Extracting audio from {os.path.basename(video_path)} to {os.path.basename(audio_path)}...")
        try:
            # Ensure the output directory exists
            os.makedirs(os.path.dirname(audio_path), exist_ok=True)
            # Check if output file already exists and remove it to avoid ffmpeg error
            if os.path.exists(audio_path):
                os.remove(audio_path)

            (
                ffmpeg
                .input(video_path)
                .output(audio_path, acodec='mp3', audio_bitrate='192k', loglevel='warning')
                .run(overwrite_output=True, capture_stdout=True, capture_stderr=True) # Capture output
            )
            print(f"Audio extracted successfully to {audio_path}")
            return audio_path
        except ffmpeg.Error as e:
            print(f"Error extracting audio using ffmpeg from {video_path}:")
            # Decode stderr for better error messages
            stderr = e.stderr.decode('utf8') if e.stderr else 'N/A'
            print(f"  FFmpeg stderr: {stderr}")
            print("  Ensure ffmpeg is installed and accessible in your system's PATH.")
            return None
        except Exception as e:
            print(f"An unexpected error occurred during audio extraction from {video_path}: {e}")
            return None

    def transcribe_audio(self, audio_path: str) -> str | None:
        """Transcribes audio file using the initialized faster-whisper model.

        Args:
            audio_path: Path to the audio file.

        Returns:
            Full transcribed text, or None if transcription failed.
        """
        if not self.model:
            print("Transcription skipped: Whisper model not initialized.")
            return None
        if not os.path.exists(audio_path):
            print(f"Error: Audio file not found at {audio_path}")
            return None

        try:
            print(f"Transcribing {os.path.basename(audio_path)}...")
            # Default beam_size is 5, VAD filter is off by default for model.transcribe
            segments, info = self.model.transcribe(audio_path, beam_size=5) # Using default beam_size

            print(f"Detected language '{info.language}' with probability {info.language_probability:.2f}")

            full_text = ""
            # Consume the generator to perform transcription and build the full text
            for segment in segments:
                full_text += segment.text + " "
                # Optional: print progress per segment if needed
                # print(f"[%.2fs -> %.2fs] {segment.text}" % (segment.start, segment.end))

            print(f"Transcription complete for {os.path.basename(audio_path)}")
            return full_text.strip()
        except Exception as e:
            print(f"Error transcribing audio {audio_path}: {e}")
            return None 