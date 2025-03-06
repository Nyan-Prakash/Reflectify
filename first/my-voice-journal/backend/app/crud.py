from google.cloud import firestore
from .database import get_db

db = get_db()

def create_voice_entry(user_id: str, transcription: str):
    """ Adds a voice entry to Firestore. """
    doc_ref = db.collection("voice_entries").document()
    doc_ref.set({
        "user_id": user_id,
        "transcription": transcription,
        "created_at": firestore.SERVER_TIMESTAMP
    })
    return doc_ref.id

def get_all_voice_entries():
    """ Retrieves all voice entries from Firestore. """
    docs = db.collection("voice_entries").stream()
    return [{**doc.to_dict(), "id": doc.id} for doc in docs]
