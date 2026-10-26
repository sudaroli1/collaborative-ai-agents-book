"""Shared settings. Change MODEL to any model you have pulled in Ollama."""
import os

MODEL = os.environ.get("BOOK_MODEL", "llama3.1:8b")
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
