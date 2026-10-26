# Collaborative Artificial Intelligence Agents: code for the book

This repository contains all the code, test sets and recorded results for the book
*Collaborative Artificial Intelligence Agents: Architectures, Workflows and Real-World
Applications* by Sudaroli Dhananjeyan (Cambridge Scholars Publishing).

Every experiment in the book runs on an ordinary laptop, with no paid services, using
[CrewAI](https://www.crewai.com/) 1.15.27 and a free local model served by
[Ollama](https://ollama.com/). The railway timetable, the passenger guide and the
operator "Deccan Rail" are invented for the book.

## Contents

| Folder | Chapter | What it contains |
|---|---|---|
| `chapter1` | 1. Foundations of AI agents | A bare model versus a first agent with a timetable tool |
| `chapter2` | 2. Teams of agents | Four crew designs, a guardrail, tracing |
| `chapter3` | 3. Workflows, memory and control | A CrewAI Flow, knowledge, memory, three versions of the checker |
| `chapter4` | 4. Agents working together | Six coordination designs, an A2A agent and client, tests and CI |
| `chapter5` | 5. Agents in the real world | A pilot measurement on 36 varied requests with two models |

Each folder has its own `README.txt` with step-by-step instructions, and a `results`
folder with the author's recorded runs, so you can compare your results with those
reported in the book.

## Quick start (Windows, macOS or Linux)

1. Install [Ollama](https://ollama.com/) and download the model:
   `ollama pull llama3.1:8b` (Chapters 4 and 5 also use `ollama pull llama3.2:3b`).
2. Create the Python environment once (CrewAI 1.15 needs Python 3.10 to 3.13):
   ```
   cd chapter1
   python -m pip install uv
   python -m uv venv .venv312 --python 3.12
   python -m uv pip install --python .venv312 "crewai[a2a]==1.15.27" pytest
   ```
3. Activate it (`.venv312\Scripts\activate` on Windows, `source .venv312/bin/activate`
   elsewhere), go to any chapter folder and run `python run_all.py --quick`.

Results will differ slightly from the book's, because language models are not fully
deterministic; the patterns, and the lessons drawn from them, should be the same.

## Licence

The code is released under the MIT Licence (see `LICENSE`). The text and illustrations of
the book are not included and remain under the publisher's copyright.
