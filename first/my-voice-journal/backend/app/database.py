import firebase_admin
from firebase_admin import credentials, firestore
import os

# Get the absolute path to the backend directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREDENTIALS_PATH = os.path.join(BASE_DIR, "firebase_config.json")  # Make sure this file exists

# Initialize Firebase only if it hasn't been initialized
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(CREDENTIALS_PATH)
        firebase_admin.initialize_app(cred)
        print("Firebase initialized successfully")
    except Exception as e:
        print(f"Error initializing Firebase: {e}")

def get_db():
    """ Returns a Firestore database instance. """
    try:
        db = firestore.client()
        return db
    except Exception as e:
        print(f"Error getting Firestore client: {e}")
        return None
