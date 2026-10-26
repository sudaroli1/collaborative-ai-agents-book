"""Listing 3-2. Knowledge: retrieval as a tool (no embeddings needed)."""
import re
from pathlib import Path
from crewai.tools import tool

GUIDE = (Path(__file__).parent / "data" / "passenger_guide.md").read_text(
    encoding="utf-8")
SECTIONS = [s.strip() for s in GUIDE.split("\n## ")[1:]]
STOP = set("a an the and or of to for on in is are can i my me do does "
           "what how will it get be with have".split())


def words(text):
    return {w for w in re.findall(r"[a-z0-9]+", text.lower())
            if w not in STOP}


@tool("search_passenger_guide")
def search_passenger_guide(question: str) -> str:
    """Search the Deccan Rail passenger guide (rules on children, senior
    citizens, luggage, refunds, pets and window seats). Returns the two
    most relevant sections."""
    q = words(question)
    ranked = sorted(SECTIONS, key=lambda s: len(q & words(s)),
                    reverse=True)
    return "\n\n".join(ranked[:2])
