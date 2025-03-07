# backend/app/services/nlp.py
import spacy
import json
import difflib
from typing import List, Dict
from datetime import datetime
import uuid

# Load spaCy English language model
nlp = spacy.load("en_core_web_sm")

def summarize_text(text: str, max_sentences: int = 3) -> str:
    """
    A simple summarization function that selects the first few sentences
    from the text if it is long. (Replace with a call to an AI model if needed.)
    """
    doc = nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
    if len(sentences) <= max_sentences:
        return text
    return " ".join(sentences[:max_sentences])

def preprocess_text(text: str, chunk_size: int = 500) -> List[str]:
    """
    Split the text into smaller chunks (by paragraphs or fixed size).
    For long texts, apply summarization to reduce input size.
    
    Returns a list of processed text chunks.
    """
    # Split by newlines assuming paragraphs; you could also split by token count.
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    processed_chunks = []
    for p in paragraphs:
        if len(p) > chunk_size:
            # If paragraph is very long, summarize it.
            p = summarize_text(p)
        processed_chunks.append(p)
    return processed_chunks

def analyze_text(text: str) -> Dict:
    """
    Analyze text for sentiment and extract events.
    
    This function first preprocesses the text (splitting and summarization),
    then extracts events from each chunk, and finally merges similar events.
    
    Returns:
        dict: Contains "sentiment_score" (a float) and "events" (a list of merged event dicts).
    """
    sentiment_score = get_sentiment(text)
    processed_chunks = preprocess_text(text)
    
    # Extract events from each processed chunk.
    events = []
    for chunk in processed_chunks:
        events.extend(extract_events(chunk))
    
    merged_events = merge_events(events)
    return {
        "sentiment_score": sentiment_score,
        "events": merged_events
    }

def get_sentiment(text: str) -> float:
    """
    Compute a basic sentiment score using a simple word-based approach.
    This method counts occurrences of predefined positive and negative words
    and returns a normalized score.
    """
    positive_words = {"good", "great", "happy", "excellent", "fortunate", "correct", "superior"}
    negative_words = {"bad", "terrible", "sad", "poor", "unfortunate", "wrong", "inferior"}
    tokens = [token.text.lower() for token in nlp(text) if token.is_alpha]
    pos_count = sum(1 for token in tokens if token in positive_words)
    neg_count = sum(1 for token in tokens if token in negative_words)
    total = len(tokens)
    return (pos_count - neg_count) / total if total > 0 else 0.0

def extract_events(text: str) -> List[Dict]:
    """
    Extract structured events from text using spaCy.
    
    For each sentence, the function extracts a rich event representation with:
      - sentence: The original sentence.
      - sentence_index: The sentence's order in the text.
      - extracted_at: ISO timestamp of extraction.
      - subject: Primary subject (if available).
      - subjects: List of all subjects identified.
      - action: The main verb in its original form.
      - action_lemma: The lemmatized form of the main verb.
      - object: Primary object (if available).
      - objects: List of all objects identified.
      - time: List of time/date entities.
      - location: List of location-related entities.
      - additional_info: List of adverbial modifiers of the main verb.
      - entities: All named entities (with their labels) found in the sentence.
    
    Args:
        text (str): The input narrative text.
    
    Returns:
        List[Dict]: A list of enriched event dictionaries (one per sentence).
    """
    doc = nlp(text)
    events = []
    
    for idx, sent in enumerate(doc.sents):
        event = {
            "event_id": str(uuid.uuid4()),
            "sentence": sent.text,
            "sentence_index": idx,
            "extracted_at": datetime.now().isoformat(),
            "subject": None,
            "subjects": [],
            "action": None,
            "action_lemma": None,
            "object": None,
            "objects": [],
            "time": [],
            "location": [],
            "additional_info": [],
            "entities": []
        }
        
        # Capture all named entities with their labels
        for ent in sent.ents:
            event["entities"].append({"text": ent.text, "label": ent.label_})
        
        # Identify the main verb (ROOT) of the sentence
        main_verb = None
        for token in sent:
            if token.dep_ == "ROOT" and token.pos_ in ("VERB", "AUX"):
                main_verb = token
                break
        if main_verb is None:
            continue
        
        event["action"] = main_verb.text
        event["action_lemma"] = main_verb.lemma_
        
        # Extract subjects (nsubj or nsubjpass) using noun chunks
        subj_chunks = [chunk for chunk in sent.noun_chunks if chunk.root.dep_ in ("nsubj", "nsubjpass")]
        subjects = [chunk.text for chunk in subj_chunks]
        if subjects:
            event["subjects"] = subjects
            event["subject"] = subjects[0]
        
        # Extract objects (dobj, attr, or pobj) using noun chunks
        obj_chunks = [chunk for chunk in sent.noun_chunks if chunk.root.dep_ in ("dobj", "attr", "pobj")]
        objects = [chunk.text for chunk in obj_chunks]
        if objects:
            event["objects"] = objects
            event["object"] = objects[0]
        
        # Extract time-related entities (DATE, TIME)
        times = [ent.text for ent in sent.ents if ent.label_ in ("TIME", "DATE")]
        event["time"] = times
        
        # Extract location-related entities (GPE, LOC, FAC)
        locations = [ent.text for ent in sent.ents if ent.label_ in ("GPE", "LOC", "FAC")]
        event["location"] = locations
        
        # Extract additional info: adverbial modifiers of the main verb
        adv_mods = [child.text for child in main_verb.children if child.dep_ == "advmod"]
        event["additional_info"] = adv_mods
        
        events.append(event)
    
    return events

def canonical_primary(event: Dict) -> str:
    """
    Create a canonical string from an event's primary details (subject, action, object).
    This helps normalize the core of the event for fuzzy comparison.
    """
    parts = []
    for key in ["subject", "action", "object"]:
        value = event.get(key)
        if value:
            parts.append(value.strip().lower())
    return " ".join(parts)

def compute_event_similarity(event1: Dict, event2: Dict) -> float:
    """
    Compute a similarity score between two events based on their canonical primary details.
    Returns a value between 0 and 1.
    """
    canon1 = canonical_primary(event1)
    canon2 = canonical_primary(event2)
    base_sim = difflib.SequenceMatcher(None, canon1, canon2).ratio()
    
    # Optionally, you can incorporate more signals (e.g., entity overlap) here.
    return base_sim

def merge_events(events: List[Dict], similarity_threshold: float = 0.6) -> List[Dict]:
    """
    Merge events that likely refer to the same occurrence.
    
    Two events are merged if the computed similarity (based on canonical primary details)
    exceeds the similarity_threshold.
    
    When merging, metadata is aggregated:
      - Increment occurrence count.
      - Update first and last mentioned timestamps.
      - Combine raw sentences and sentence indices.
      - Merge lists (subjects, objects, time, location, additional_info, entities) uniquely.
    """
    merged = []
    for event in events:
        found = False
        for m_ev in merged:
            if compute_event_similarity(m_ev, event) >= similarity_threshold:
                # Merge event into the existing merged event.
                m_ev["occurrences"] += 1
                m_ev["last_mentioned"] = datetime.now().isoformat()
                if event["sentence"] not in m_ev.get("raw_sentences", []):
                    m_ev.setdefault("raw_sentences", []).append(event["sentence"])
                    m_ev.setdefault("sentence_indices", []).append(event["sentence_index"])
                # Merge subjects and objects uniquely.
                m_ev["subjects"] = list(set(m_ev["subjects"] + event["subjects"]))
                if not m_ev["subject"] and event["subject"]:
                    m_ev["subject"] = event["subject"]
                m_ev["objects"] = list(set(m_ev["objects"] + event["objects"]))
                if not m_ev["object"] and event["object"]:
                    m_ev["object"] = event["object"]
                # Merge other lists uniquely.
                m_ev["time"] = list(set(m_ev["time"] + event["time"]))
                m_ev["location"] = list(set(m_ev["location"] + event["location"]))
                m_ev["additional_info"] = list(set(m_ev["additional_info"] + event["additional_info"]))
                # Merge entities uniquely (using lowercase text for comparison).
                existing_entities = {(ent["text"].lower(), ent["label"]) for ent in m_ev["entities"]}
                for ent in event["entities"]:
                    if (ent["text"].lower(), ent["label"]) not in existing_entities:
                        m_ev["entities"].append(ent)
                        existing_entities.add((ent["text"].lower(), ent["label"]))
                found = True
                break
        if not found:
            new_event = event.copy()
            new_event["occurrences"] = 1
            new_event["first_mentioned"] = event["extracted_at"]
            new_event["last_mentioned"] = event["extracted_at"]
            new_event["raw_sentences"] = [event["sentence"]]
            new_event["sentence_indices"] = [event["sentence_index"]]
            merged.append(new_event)
    return merged
