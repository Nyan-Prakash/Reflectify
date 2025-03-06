import os
from app.services.transcription import transcribe_audio
from google.cloud import speech
from google.oauth2 import service_account

def test_credentials():
    """Test if we can load the credentials"""
    try:
        cred_path = os.path.join(os.path.dirname(__file__), "google_speech_credentials.json")
        print(f"Looking for credentials at: {cred_path}")
        
        if not os.path.exists(cred_path):
            print("❌ Credentials file not found!")
            return False
            
        credentials = service_account.Credentials.from_service_account_file(cred_path)
        print("✅ Credentials loaded successfully")
        
        # Print project ID from credentials
        print(f"Project ID: {credentials.project_id}")
        return True
    except Exception as e:
        print(f"❌ Error loading credentials: {e}")
        return False

def test_audio_file(file_path):
    """Test if we can read the audio file"""
    try:
        if not os.path.exists(file_path):
            print(f"❌ Audio file not found at {file_path}")
            return False
            
        size = os.path.getsize(file_path)
        print(f"✅ Audio file found, size: {size} bytes")
        
        with open(file_path, "rb") as f:
            content = f.read()
            print(f"✅ Successfully read {len(content)} bytes")
        return True
    except Exception as e:
        print(f"❌ Error reading audio file: {e}")
        return False

def test_transcription(file_path):
    """Test the full transcription process"""
    try:
        print("\n🔍 Testing transcription...")
        result = transcribe_audio(file_path)
        print(f"Result: {result}")
        return True
    except Exception as e:
        print(f"❌ Transcription error: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Starting transcription tests...\n")
    
    # Test credentials
    print("1. Testing credentials...")
    if not test_credentials():
        print("❌ Credential test failed, stopping tests")
        exit(1)
    
    # Create a test audio file if needed
    test_file = os.path.join(os.path.dirname(__file__), "something.flac")
    
    # Test audio file
    print("\n2. Testing audio file...")
    if not test_audio_file(test_file):
        print("❌ Audio file test failed, stopping tests")
        exit(1)
    
    # Test transcription
    print("\n3. Testing transcription...")
    test_transcription(test_file) 