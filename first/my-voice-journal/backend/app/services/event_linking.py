# backend/app/services/event_linking.py
import json

def link_events(existing_events_str: str, new_events: list):
    """
    Combine old events with newly detected ones (very naive approach).
    """
    if not existing_events_str:
        existing_events = []
    else:
        existing_events = json.loads(existing_events_str)

    for event in new_events:
        if event not in existing_events:
            existing_events.append(event)

    return json.dumps(existing_events)
