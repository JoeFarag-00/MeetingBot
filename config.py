import os

# --- Directories ---
VIDEO_DIR = "Meetings"  # Directory containing video files
TRANSCRIPT_DIR = "transcripts"  # Directory to save full transcripts
SUMMARY_DIR = "summaries"  # Directory to save summaries
AUDIO_TEMP_DIR = "temp_audio" # Directory for temporary audio files

# --- Faster Whisper Settings ---
MODEL_SIZE = "large-v3"  # Options: "tiny", "base", "small", "medium", "large-v2", "large-v3", "distil-large-v3", etc.
DEVICE = "cuda"  # "cuda" or "cpu"
COMPUTE_TYPE = "float16"  # "float16", "int8_float16", "int8" (CPU supports "int8" and "float32")
# BEAM_SIZE = 5 # Default is 5, kept here for reference

# --- Groq Settings ---
GROQ_MODEL = "llama3-70b-8192" # Or "mixtral-8x7b-32768", "gemma-7b-it" etc.
# Consider adding temperature, max_tokens here if needed often
# GROQ_TEMPERATURE = 0.7
# GROQ_MAX_TOKENS = 500

# --- File Handling ---
SUPPORTED_VIDEO_EXTENSIONS = ('.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv') # Add other extensions if needed

# --- API Keys (Loaded from .env) ---
# Ensure you have a .env file in the root directory with GROQ_API_KEY=your_key
# Example .env content:
# GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx 