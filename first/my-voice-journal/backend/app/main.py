from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import uuid
import os
import json
from .database import get_db
from .services.transcription import transcribe_audio
from .services.nlp import analyze_text, extract_events
from .services.event_linking import link_events
from firebase_admin import firestore as admin_firestore

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up upload directory
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "uploaded_audios")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Get credentials path
CRED_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "google_speech_credentials.json")

# Remove the Firestore initialization code and just use get_db
db = get_db()

@app.post("/api/entries/upload")
async def upload_audio(file: UploadFile = File(...)):
    try:
        print(f"Received file: {file.filename}, content_type: {file.content_type}")
        
        # Create unique filename (keep original extension)
        extension = file.filename.split(".")[-1]
        file_name = f"{uuid.uuid4()}.{extension}"
        audio_path = os.path.join(UPLOAD_DIR, file_name)
        
        # Save the file
        content = await file.read()
        if len(content) == 0:
            raise ValueError("Received empty file")
            
        with open(audio_path, "wb") as f:
            f.write(content)
        
        file_size = os.path.getsize(audio_path)
        print(f"File saved, size: {file_size} bytes")
        
        if file_size == 0:
            raise ValueError("File was saved but is empty")

        # Transcribe
        transcription = transcribe_audio(audio_path)
        
        # Extract events and analyze sentiment
        if transcription:
            analysis = analyze_text(transcription)
            events = extract_events(transcription)
        else:
            analysis = {"sentiment_score": 0, "events": []}
            events = []

        # Only try to save to Firestore if it's initialized
        if db is not None:
            try:
                doc_ref = db.collection("voice_entries").document()
                doc_data = {
                    "audio_file_path": audio_path,
                    "transcription": transcription or "No transcription available",
                    "sentiment_score": analysis["sentiment_score"],
                    "events_tagged": link_events("[]", events),
                    "created_at": admin_firestore.SERVER_TIMESTAMP
                }
                doc_ref.set(doc_data)
                entry_id = doc_ref.id
                print(f"Successfully saved to Firestore with ID: {entry_id}")
            except Exception as e:
                print(f"Firestore error: {e}")
                entry_id = None
        else:
            print("Database not initialized")
            entry_id = None

        return {
            "status": "success",
            "entry_id": entry_id,
            "transcription": transcription,
            "events": events,
            "message": "Audio uploaded and processed successfully"
        }

    except Exception as e:
        print(f"Error in upload_audio: {str(e)}")
        return {"status": "error", "message": str(e)}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/timeline")
def get_timeline():
    """
    Returns all entries in descending date order (most recent first).
    """
    docs = db.collection("voice_entries").order_by("created_at", direction=admin_firestore.Query.DESCENDING).stream()
    return [{"id": doc.id, **doc.to_dict()} for doc in docs]

@app.get("/api/events/main")
def get_main_events():
    """
    Retrieves main events from Firestore and counts their occurrences.
    Converts them to a hashable structure for counting, then back to JSON-friendly data.
    """

    def make_hashable(item):
        """
        Recursively convert lists and dictionaries to tuples so that the
        entire structure becomes hashable (so we can use it as a dict key).
        """
        if isinstance(item, (list, tuple)):
            return tuple(make_hashable(e) for e in item)
        elif isinstance(item, dict):
            # Sort the items to ensure consistent ordering for the tuple
            return tuple(sorted((k, make_hashable(v)) for k, v in item.items()))
        else:
            return item

    def make_json_friendly(item):
        """
        Recursively convert tuples back into lists (and so on),
        ensuring that the final data is JSON-serializable.
        """
        if isinstance(item, tuple):
            return [make_json_friendly(sub) for sub in item]
        elif isinstance(item, list):
            return [make_json_friendly(sub) for sub in item]
        elif isinstance(item, dict):
            return {k: make_json_friendly(v) for k, v in item.items()}
        else:
            return item

    docs = db.collection("voice_entries").stream()
    events_map = {}

    for doc in docs:
        data = doc.to_dict()
        if "events_tagged" in data and data["events_tagged"]:
            try:
                event_list = json.loads(data["events_tagged"])
            except Exception as e:
                print(f"Error parsing events_tagged: {e}")
                event_list = []
            for ev in event_list:
                # Convert dictionaries to a hashable structure for counting.
                key = make_hashable(ev)
                events_map[key] = events_map.get(key, 0) + 1

    # Filter events with multiple occurrences (you can adjust the threshold if needed).
    main_events = [k for k, count in events_map.items() if count > 1]

    # Convert the "main events" from tuple form back to JSON-friendly form.
    main_events_readable = [make_json_friendly(m) for m in main_events]

    # Convert *all* keys in events_map to JSON strings (so the front-end can parse them).
    events_map_readable = {}
    for key, count in events_map.items():
        # key might be a nested tuple/dict structure, so convert it first.
        json_friendly_key = make_json_friendly(key)
        # Then turn it into a JSON string (which the frontend can parse).
        key_str = json.dumps(json_friendly_key)
        events_map_readable[key_str] = count

    return {
        "main_events": main_events_readable,
        "all_events": events_map_readable
    }
