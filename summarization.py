import os
from groq import Groq, APIError
from dotenv import load_dotenv
import config
import math # Added for ceiling division

# --- Constants for Chunking ---
# Adjust these based on testing and observed token limits vs character counts
# Aim for chunk size well below the API limit (e.g., 6k tokens might roughly be 15k-20k chars)
TARGET_CHUNK_CHAR_LENGTH = 10000
CHUNK_OVERLAP_CHAR_LENGTH = 500 # Overlap to maintain context

class Summarizer:
    """Handles text summarization using the Groq API, with chunking for large texts."""

    def __init__(self):
        self.model_name = config.GROQ_MODEL
        self.client = self._initialize_client()

    def _initialize_client(self):
        """Initializes the Groq client."""
        print("Initializing Groq client...")
        load_dotenv()
        api_key = os.environ.get("GROQ_API_KEY")

        if not api_key:
            print("Error: GROQ_API_KEY not found in environment variables.")
            print("Please create a .env file in the project root with GROQ_API_KEY=your_key or set the environment variable.")
            return None

        try:
            client = Groq(api_key=api_key)
            print(f"Groq client initialized successfully for model: {self.model_name}")
            return client
        except APIError as e:
            print(f"Groq API Error initializing client: {e.status_code} - {e.message}")
            if e.status_code == 401:
                 print("Hint: Check if your GROQ_API_KEY is correct and active.")
            elif e.status_code == 429:
                 print("Hint: You might have hit the Groq API rate limits.")
            return None
        except Exception as e:
            print(f"Error initializing Groq client: {e}")
            return None

    def _chunk_text(self, text: str, chunk_size: int, overlap: int) -> list[str]:
        """Splits text into overlapping chunks."""
        if len(text) <= chunk_size:
            return [text]

        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunks.append(text[start:end])
            start += chunk_size - overlap
            if start + overlap >= len(text): # Prevent adding a tiny overlapping chunk at the very end
                 break
        # Ensure the last part of the text is included if missed
        if start < len(text) and not text[start:].isspace():
             last_chunk_start = max(0, len(text) - chunk_size) # Ensure last chunk is full size if possible
             chunks.append(text[last_chunk_start:])


        # Remove duplicates that might occur if overlap logic grabs the same final chunk
        unique_chunks = []
        for chunk in chunks:
            if not unique_chunks or unique_chunks[-1] != chunk:
                unique_chunks.append(chunk)

        return unique_chunks


    def _call_groq_api(self, prompt_text: str, system_message: str, max_tokens: int, temperature: float) -> str | None:
        """Helper function to call the Groq API for summarization."""
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt_text}
                ],
                model=self.model_name,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            result = chat_completion.choices[0].message.content
            return result.strip()
        except APIError as e:
            print(f"Groq API Error during summarization call: {e.status_code} - {e.message}")
            # Specific handling for rate limits / size issues if needed
            if e.status_code == 413 or 'rate_limit_exceeded' in str(e.message) or 'Request too large' in str(e.message):
                 print("  >> Suggestion: Try reducing TARGET_CHUNK_CHAR_LENGTH in summarization.py or check Groq tier limits.")
            return None
        except Exception as e:
            print(f"Error during Groq API call: {e}")
            return None

    def summarize_text(self, text: str, max_tokens: int = 500, temperature: float = 0.7) -> str | None:
        """Summarizes text, handling large inputs via chunking and iterative summarization."""
        if not self.client:
            print("Summarization skipped: Groq client not initialized.")
            return None
        if not text or text.isspace():
            print("Cannot summarize empty or whitespace-only text.")
            return None

        print(f"Starting summarization process using Groq ({self.model_name})...")

        # --- Chunking ---
        chunks = self._chunk_text(text, TARGET_CHUNK_CHAR_LENGTH, CHUNK_OVERLAP_CHAR_LENGTH)
        num_chunks = len(chunks)
        print(f"Text length: {len(text)} chars. Split into {num_chunks} chunk(s).")

        if num_chunks == 0:
             print("Error: Text chunking resulted in zero chunks.")
             return None

        # --- Summarize Chunks ---
        chunk_summaries = []
        for i, chunk in enumerate(chunks):
            print(f"Summarizing chunk {i+1}/{num_chunks} (length: {len(chunk)} chars)...")
            # Slightly different prompt for individual chunks vs final summary
            chunk_prompt = (
                "You are an expert meeting summarizer. Summarize the following segment of a meeting transcript into concise key points or bullet points ONLY. Mention the names and companies involved if any."
                "Focus specifically on the main topics discussed, key decisions made, and any action items assigned within this segment.\nSummarize in Arabic and English."
                "Do not add introductory or concluding phrases like 'In this segment...' unless necessary for context.\n"
                "Transcript Segment:\n---\n"
                f"{chunk}"
                "\n---\nKey Points Summary:"
            )
            system_msg = "You are an AI assistant specialized in summarizing segments of meeting transcripts."
            chunk_summary = self._call_groq_api(chunk_prompt, system_msg, max_tokens, temperature)

            if chunk_summary:
                chunk_summaries.append(chunk_summary)
                print(f"Chunk {i+1} summary generated.")
            else:
                print(f"Failed to summarize chunk {i+1}. Skipping this chunk.")
                # Decide if we should fail the whole process or continue
                # return None # Option: Fail completely if one chunk fails

        if not chunk_summaries:
            print("Summarization failed: No summaries could be generated from the chunks.")
            return None

        # --- Combine and Final Summary ---
        combined_summary = "\n\n---\n\n".join(chunk_summaries) # Join with separator for clarity

        if num_chunks == 1:
            print("Single chunk processed. Returning its summary directly.")
            return combined_summary # No need for final pass if only one chunk
        else:
            print(f"Combining {len(chunk_summaries)} chunk summaries for final pass...")
            # Prompt for the final summarization pass
            final_prompt = (
                "You are an expert meeting summarizer. The following text consists of several partial summaries derived from different segments of a longer meeting transcript. "
                "Synthesize these partial summaries into a single, coherent, and concise final summary. "
                "Ensure all critical information (main topics, decisions, actions) is retained, remove redundancy, and present it logically.\nSummarize in Arabic and English.\n"
                "Partial Summaries:\n---\n"
                f"{combined_summary}"
                "\n---\nConsolidated Final Summary:"
            )
            system_msg = "You are an AI assistant skilled at consolidating multiple partial summaries into a final, coherent summary."

            # Use slightly more tokens potentially for the final pass if needed
            final_max_tokens = max_tokens * 2 # Example: Allow more room for consolidation

            final_summary = self._call_groq_api(final_prompt, system_msg, final_max_tokens, temperature)

            if final_summary:
                print("Final consolidated summary generated.")
                return final_summary
            else:
                print("Failed to generate final consolidated summary. Returning combination of chunk summaries as fallback.")
                # Fallback: Return the combined chunk summaries if final pass fails
                return combined_summary 