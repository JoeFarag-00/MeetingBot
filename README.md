# Meeting Transcriber & Summarizer

An AI-powered tool that automatically transcribes and summarizes bilingual (Arabic/English) meetings into key points. The system uses Faster Whisper for high-quality transcription and Groq's LLM for intelligent summarization.

## Features

- 🎥 **Video Processing**: Supports multiple video formats (mp4, mov, avi, mkv, wmv, flv)
- 🎙️ **High-Quality Transcription**: Uses Faster Whisper's large-v3 model for accurate speech-to-text
- 🌐 **Bilingual Support**: Handles both Arabic and English content
- 📝 **Smart Summarization**: Generates concise key points in both Arabic and English
- 🔄 **Chunking System**: Intelligently processes long meetings by breaking them into manageable segments
- 💾 **File Management**: Automatically organizes transcripts and summaries
- ⚡ **GPU Acceleration**: Supports CUDA for faster processing (when available)

## Prerequisites

- Python 3.8 or higher
- FFmpeg installed on your system
- NVIDIA GPU with CUDA support (recommended for faster processing)
- Groq API key

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd meeting-transcriber-summarizer
```

2. Install required Python packages:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root with your Groq API key:
```
GROQ_API_KEY=your_groq_api_key_here
```

4. Install FFmpeg:
   - **Windows**: Download from [FFmpeg website](https://ffmpeg.org/download.html) and add to PATH
   - **Linux**: `sudo apt-get install ffmpeg`
   - **macOS**: `brew install ffmpeg`

## Configuration

The `config.py` file contains important settings:

- **Video Directory**: Where to look for video files
- **Model Settings**: Whisper model size and device settings
- **Groq Settings**: LLM model selection
- **File Extensions**: Supported video formats

## Usage

1. Place your meeting video files in the `Meetings` directory

2. Run the main script:
```bash
python main.py
```

3. The system will:
   - Extract audio from videos
   - Transcribe the audio using Faster Whisper
   - Generate bilingual summaries using Groq
   - Save transcripts and summaries in their respective directories

## Output Structure

- `Meetings/`: Input video files
- `transcripts/`: Full meeting transcripts
- `summaries/`: Bilingual summaries in both Arabic and English
- `temp_audio/`: Temporary audio files (automatically cleaned up)

## Performance Considerations

- For optimal performance, use a CUDA-capable GPU
- The system uses Faster Whisper's large-v3 model by default
- Long meetings are automatically chunked for efficient processing
- Temporary audio files are automatically cleaned up after processing

## Troubleshooting

1. **CUDA Issues**:
   - Ensure NVIDIA drivers are up to date
   - Verify CUDA installation
   - Check GPU memory availability

2. **FFmpeg Errors**:
   - Verify FFmpeg installation
   - Check if FFmpeg is in system PATH
   - Ensure video files are not corrupted

3. **Groq API Issues**:
   - Verify API key in `.env` file
   - Check API rate limits
   - Ensure internet connectivity

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[Add your chosen license here]

## Acknowledgments

- [Faster Whisper](https://github.com/guillaumekln/faster-whisper) for the transcription engine
- [Groq](https://groq.com/) for the LLM API
- [FFmpeg](https://ffmpeg.org/) for audio processing 