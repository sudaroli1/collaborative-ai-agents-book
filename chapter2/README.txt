CHAPTER 2 CODE - HOW TO RUN
===========================
Uses the same Python environment and Ollama model as Chapter 1.
The timetable in data/timetable.csv is invented for the book.

1. Make sure the Ollama app is running.
2. Open Command Prompt and go to this folder:
       cd %USERPROFILE%\Desktop\Preparation\Book_Proposal\code\chapter2
3. Activate the Chapter 1 environment:
       ..\chapter1\.venv312\Scripts\activate
4. Quick check (about 8 minutes):
       python run_all.py --quick
5. Full experiment (about 45 minutes):
       python run_all.py
   When it says "All done", tell Claude.

Files
-----
agents.py          Listing 2-1  Nova (recommends) and Rin (checks)
tasks.py           Listing 2-2  the recommend and check tasks
guardrail.py       Listing 2-3  a guardrail written in code
crews.py           Listing 2-4  four designs: single, guarded, checked, managed
trace_listener.py  Listing 2-5  records every step for debugging
requests.json      12 test requests with their correct answers
runner.py, run_all.py  experiment scripts (not printed in the book)
