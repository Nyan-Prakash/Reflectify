# backend/app/services/nlp.py
import spacy
nlp = spacy.load("en_core_web_sm")

def analyze_text(text: str):
    doc = nlp(text)
    # Basic placeholder sentiment score (you can integrate a more sophisticated approach)
    # For demonstration, let's do a naive approach: polarity based on certain keywords
    positive_words = ["good", "happy", "great", "amazing"]
    negative_words = ["bad", "sad", "terrible", "awful"]

    score = 0.0
    for token in doc:
        if token.text.lower() in positive_words:
            score += 1
        elif token.text.lower() in negative_words:
            score -= 1

    # Extract events: for simplicity, look for named entities as potential "events"
    # In a real app, you’d build more advanced logic here
    events = [ent.text for ent in doc.ents]

    return score, events
