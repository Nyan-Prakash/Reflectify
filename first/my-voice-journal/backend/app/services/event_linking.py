# backend/app/services/event_linking.py
import json
import difflib
from typing import List, Dict
from datetime import datetime

# Optional: Using SentenceTransformers for event embeddings.
try:
    from sentence_transformers import SentenceTransformer, util
    model = SentenceTransformer('all-MiniLM-L6-v2')
except ImportError:
    model = None  # Fallback if the embedding model is not available

def normalize_field(text: str) -> str:
    """
    Normalize text by lowercasing, stripping, and removing common extra words.
    Customize this function as needed to further normalize your fields.
    """
    text = text.lower().strip()
    # Example: Remove trailing " ride" from object strings.
    if text.endswith(" ride"):
        text = text[:-5].strip()
    return text

def canonical_event(event: Dict) -> str:
    """
    Create a canonical string representation of an event by normalizing key fields.
    This representation concatenates normalized subject, action, object, and location.
    """
    parts = []
    for key in ["subject", "action", "object", "location"]:
        value = event.get(key)
        if value and isinstance(value, str):
            parts.append(normalize_field(value))
    return " ".join(parts)

def get_event_embedding(event: Dict):
    """
    Generate an embedding for an event using its canonical string.
    Returns None if the embedding model is not available.
    """
    if model is None:
        return None
    canon = canonical_event(event)
    return model.encode(canon, convert_to_tensor=True)

def similar_events(event_str1: str, event_str2: str, embedding1=None, embedding2=None) -> bool:
    """
    Determine if two event canonical strings are similar enough to be considered the same.
    
    This function first attempts to use cosine similarity between embeddings (if available)
    and then falls back on fuzzy string matching and word overlap.
    """
    # If embeddings are provided, use cosine similarity.
    if embedding1 is not None and embedding2 is not None:
        cosine_sim = util.cos_sim(embedding1, embedding2).item()
        EMBEDDING_THRESHOLD = 0.8  # Adjust as needed
        if cosine_sim >= EMBEDDING_THRESHOLD:
            return True

    # Fuzzy string matching ratio
    fuzzy_ratio = difflib.SequenceMatcher(None, event_str1, event_str2).ratio()
    
    # Calculate word overlap ratio
    words1 = set(event_str1.split())
    words2 = set(event_str2.split())
    union_words = words1.union(words2)
    word_overlap = (len(words1.intersection(words2)) / len(union_words)) if union_words else 0

    FUZZY_THRESHOLD = 0.65  # Lowered threshold to allow more leniency
    WORD_OVERLAP_THRESHOLD = 0.5

    return fuzzy_ratio >= FUZZY_THRESHOLD or word_overlap >= WORD_OVERLAP_THRESHOLD

def link_events(existing_events_str: str, new_events: List[Dict]) -> str:
    """
    Link new events with existing ones, maintaining metadata about occurrences.
    
    Each event is a dictionary with the following fields:
      - subject: who or what performed the action,
      - action: the main verb describing the event,
      - object: what or who was affected by the action,
      - time: when the event happened (if available),
      - location: where the event took place (if available),
      - additional_info: any extra contextual details.
      
    Additionally, each event is enriched with metadata:
      - occurrences: count of event occurrences,
      - first_mentioned: ISO timestamp when the event was first mentioned.
    
    The function uses a canonical representation of each event and a similarity check
    (via embedding cosine similarity if available and fuzzy matching) to determine if a new event
    should be merged with an existing one.
    
    Args:
        existing_events_str (str): JSON string of existing events.
        new_events (List[Dict]): A list of new event dictionaries.
    
    Returns:
        str: A JSON string of the updated events list.
    """
    try:
        existing_events = json.loads(existing_events_str) if existing_events_str else []
    except json.JSONDecodeError:
        existing_events = []
    
    # Ensure each existing event has the proper metadata.
    for event in existing_events:
        if "occurrences" not in event:
            event["occurrences"] = 1
        if "first_mentioned" not in event or not event["first_mentioned"]:
            event["first_mentioned"] = datetime.now().isoformat()
    
    for new_event in new_events:
        new_event_canonical = canonical_event(new_event)
        new_embedding = get_event_embedding(new_event) if model is not None else None
        
        matching_event = None
        for existing_event in existing_events:
            existing_event_canonical = canonical_event(existing_event)
            existing_embedding = get_event_embedding(existing_event) if model is not None else None
            
            if similar_events(existing_event_canonical, new_event_canonical, existing_embedding, new_embedding):
                matching_event = existing_event
                break
        
        if matching_event:
            matching_event["occurrences"] = matching_event.get("occurrences", 1) + 1
            if not matching_event.get("first_mentioned"):
                matching_event["first_mentioned"] = datetime.now().isoformat()
        else:
            new_event["occurrences"] = 1
            new_event["first_mentioned"] = datetime.now().isoformat()
            existing_events.append(new_event)
    
    return json.dumps(existing_events)
