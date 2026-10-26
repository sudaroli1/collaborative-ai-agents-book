"""Listing 3-3. Long-term memory: preferences that survive between runs."""
import json
from pathlib import Path
from crewai.tools import tool

STORE = Path(__file__).parent / "data" / "memory.json"


@tool("remember_preference")
def remember_preference(preference: str) -> str:
    """Save a lasting travel preference of the traveller, in one short
    sentence, so that it can be used in future bookings."""
    notes = json.loads(STORE.read_text()) if STORE.exists() else []
    notes.append(preference)
    STORE.write_text(json.dumps(notes, indent=1))
    return "Saved."


@tool("recall_preferences")
def recall_preferences(topic: str = "travel") -> str:
    """Return every saved travel preference of the traveller. Always
    check these before recommending a train."""
    notes = json.loads(STORE.read_text()) if STORE.exists() else []
    return "\n".join(notes) if notes else "No saved preferences."
