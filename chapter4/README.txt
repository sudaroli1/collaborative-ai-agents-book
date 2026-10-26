CHAPTER 4 CODE - HOW TO RUN
===========================
Uses the same Python environment and Ollama model as Chapters 1-3.

One-time setup (about 5 minutes)
  a. Add the A2A and testing packages to the book's environment. In
     Command Prompt, in this folder:
         uv pip install --python ..\chapter1\.venv312 "crewai[a2a]==1.15.27" pytest
  b. Download the small model used in Section 4.4 (about 2 GB):
         ollama pull llama3.2:3b

Running
  1. Make sure the Ollama app is running.
  2. cd %USERPROFILE%\Desktop\Preparation\Book_Proposal\code\chapter4
  3. ..\chapter1\.venv312\Scripts\activate
  4. Quick check (about 10 minutes):   python run_all.py --quick
  5. Full experiment (about 75 minutes): python run_all.py
     When it says "All done", tell Claude.

Files
-----
team4.py            Listing 4-1  researcher, writer, manager; Leg hand-off
designs4.py         Listing 4-2  five ways to coordinate the same job
rules4.py           Listing 4-3  booking rules as plain functions
workflow4.py        Listing 4-4  coordination by code (a Flow)
a2a_server4.py      Listing 4-5  the trip planner published as an A2A agent
a2a_client4.py      Listing 4-6  discovering and using the A2A agent
tests\test_rules.py Listing 4-7  unit tests (no model)
tests\test_eval.py  Listing 4-8  the evaluation set as a test
ci\agents.yml      Listing 4-9  continuous integration (GitHub Actions)
trips.json          six return-trip requests with correct answers
runner4.py, run_all.py, lib\   experiment scripts (not printed)
