import os
from google.cloud import speech
from google.oauth2 import service_account

def transcribe_audio(audio_path):
    try:
        # Debug print
        print(f"\n=== Starting Transcription Process ===")
        print(f"Input file: {audio_path}")
        
        # Check file
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        file_size = os.path.getsize(audio_path)
        print(f"File size: {file_size} bytes")
        
        if file_size == 0:
            raise ValueError("Audio file is empty")

        # Get credentials
        script_dir = os.path.dirname(os.path.realpath(__file__))
        cred_path = os.path.join(script_dir, "..", "..", "google_speech_credentials.json")
        print(f"Looking for credentials at: {cred_path}")
        
        if not os.path.exists(cred_path):
            raise FileNotFoundError(f"Credentials not found at {cred_path}")

        # Initialize client
        print("Initializing Speech-to-Text client...")
        credentials = service_account.Credentials.from_service_account_file(cred_path)
        client = speech.SpeechClient(credentials=credentials)

        # Read audio content
        print("Reading audio file...")
        with open(audio_path, "rb") as audio_file:
            content = audio_file.read()
        print(f"Read {len(content)} bytes from audio file")

        # Create recognition audio
        print("Creating RecognitionAudio object...")
        audio = speech.RecognitionAudio(content=content)
        
        # Configure recognition based on file type
        if audio_path.lower().endswith('.webm'):
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
                sample_rate_hertz=48000,
                language_code="en-US",
                enable_automatic_punctuation=True,
                audio_channel_count=1,
            )
        else:  # For WAV files
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,  # Standard rate for WAV files
                language_code="en-US",
                enable_automatic_punctuation=True,
                audio_channel_count=1,
                enable_word_time_offsets=True,
            )

        print(f"Using config: {config}")

        # Make API call
        print("\nSending request to Google Speech-to-Text API...")
        response = client.recognize(config=config, audio=audio)
        print("Received response from API")
        
        # Process results
        if not response.results:
            print("No transcription results received")
            return "No transcription available"
            
        transcript = response.results[0].alternatives[0].transcript
        confidence = response.results[0].alternatives[0].confidence
        
        print(f"\nTranscription successful!")
        print(f"Confidence: {confidence}")
        print(f"Transcript: {transcript}")
        
        return transcript

    except Exception as e:
        print(f"\n❌ Error in transcribe_audio: {str(e)}")
        return f"Transcription error: {str(e)}"

# **Run the function with a sample audio file**
if __name__ == "__main__":
    # Adjust the path based on your project structure
    script_dir = os.path.dirname(os.path.realpath(__file__))  # backend/app/services
    audio_path = os.path.join(script_dir, "..", "..", "testing", "sample.wav")  # Adjust as needed

    if not os.path.exists(audio_path):
        print(f"Error: Audio file not found at {audio_path}")
    else:
        transcription = transcribe_audio(audio_path)
        print("\nTranscription:\n", transcription)
