"""Listing 1-1. A bare language model: it can answer, but it cannot act."""
from crewai import LLM
from config import MODEL, OLLAMA_URL

llm = LLM(model=f"ollama/{MODEL}", base_url=OLLAMA_URL, temperature=0)

QUESTION = ("Which trains can I take from Bengaluru to Mysuru on "
            "Saturday morning, and which one has a free window seat?")


def ask():
    return llm.call([{"role": "user", "content": QUESTION}])


if __name__ == "__main__":
    print(ask())
