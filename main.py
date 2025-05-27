import time
import os
from tqdm import tqdm

from file_handler import FileHandler
from transcription import Transcriber
from summarization import Summarizer
import config 

def main():
    """Main function to orchestrate the video processing pipeline."""
    start_time = time.time()

    # --- Initialization --- #
    print("--- Starting Video Processing Pipeline ---")
    file_handler = FileHandler()
    file_handler.create_directories() # Ensure output directories exist

    # Initialize services (potential failure points)
    transcriber = Transcriber()
    summarizer = Summarizer()

    # Check if initializations were successful
    if not transcriber.model:
        print("Critical Error: Failed to initialize the Transcription model. Exiting.")
        return
    if not summarizer.client:
        print("Critical Error: Failed to initialize the Summarization client (Groq). Exiting.")
        print("Please ensure your GROQ_API_KEY is set correctly in a .env file.")
        return

    print("\n--- Locating Video Files ---")
    video_files = file_handler.get_video_files()

    if not video_files:
        print(f"No videos found in '{config.VIDEO_DIR}'. Please add videos and rerun. Exiting.")
        return

    # --- Core Processing Logic --- #
    print(f"\n--- Processing {len(video_files)} Video File(s) ---")
    processed_successfully = 0
    failed_files = 0

    for video_file in tqdm(video_files, desc="Overall Progress", unit="video"):
        print(f"\n--- Processing: {video_file} ---")
        video_path, audio_path, transcript_path, summary_path = file_handler.get_paths(video_file)

        audio_extracted = False
        transcription_successful = False
        summary_successful = False
        current_file_failed = False
        transcription = None # Initialize transcription variable

        # --- Check for Existing Transcript ---
        if os.path.exists(transcript_path):
            print(f"Found existing transcript: {transcript_path}. Reading content.")
            try:
                with open(transcript_path, 'r', encoding='utf-8') as f:
                    transcription = f.read()
                if transcription:
                    print("Successfully read existing transcript.")
                    transcription_successful = True
                    # Skip audio extraction and transcription steps
                    audio_extracted = False # We didn't extract in this run
                else:
                    print("Existing transcript file is empty. Proceeding with extraction/transcription.")
                    # Proceed as if file didn't exist or was invalid
            except Exception as e:
                print(f"Error reading existing transcript file {transcript_path}: {e}. Proceeding with extraction/transcription.")
                # Proceed as if file didn't exist or was invalid

        # --- Step 1: Extract Audio --- #
        # Only run if transcript wasn't successfully read from existing file
        if not transcription_successful:
            extracted_audio_path = transcriber.extract_audio(video_path, audio_path)
            if not extracted_audio_path:
                print(f"Failed Step: Audio extraction for {video_file}.")
                current_file_failed = True
            else:
                audio_extracted = True

            # --- Step 2: Transcribe Audio --- #
            if not current_file_failed:
                transcription = transcriber.transcribe_audio(extracted_audio_path)
                if transcription is None:
                    print(f"Failed Step: Transcription for {video_file}.")
                    current_file_failed = True
                else:
                    transcription_successful = True
                    # --- Step 3: Save Transcript --- #
                    # Save the newly generated transcript
                    file_handler.save_text(transcription, transcript_path)

        # --- Step 4: Summarize Transcript --- #
        # Run if transcription (either new or loaded) was successful
        if transcription_successful and not current_file_failed:
            summary = summarizer.summarize_text(transcription)
            if summary is None:
                print(f"Failed Step: Summary generation for {video_file}.")
                # Decide if this counts as a full file failure or just partial success
                # current_file_failed = True # Optional: Mark as failed if summary is crucial
            else:
                summary_successful = True
                # --- Step 5: Save Summary --- #
                file_handler.save_text(summary, summary_path)

        # --- Step 6: Clean up temp audio --- #
        if audio_extracted: # Attempt cleanup even if subsequent steps failed
            file_handler.cleanup_temp_audio(extracted_audio_path)

        # --- Update Counters --- #
        if current_file_failed:
            failed_files += 1
            print(f"--- Failed processing: {video_file} ---")
        elif transcription_successful: # Consider successful if at least transcription worked
             processed_successfully += 1
             print(f"--- Finished processing: {video_file} ---")
        else: # Should not happen if logic is correct, but as a fallback
            failed_files += 1
            print(f"--- Unknown failure state for: {video_file} ---")


    # --- Final Report --- #
    end_time = time.time()
    total_time = end_time - start_time
    print(f"\n--- Pipeline Finished ---")
    print(f"Total video files found: {len(video_files)}")
    print(f"Successfully processed (transcribed): {processed_successfully}")
    print(f"Failed processing: {failed_files}")
    print(f"Total execution time: {total_time:.2f} seconds")

if __name__ == "__main__":
    main() 