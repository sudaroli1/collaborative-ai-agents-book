CHAPTER 3 CODE - HOW TO RUN
===========================
Uses the same Python environment and Ollama model as Chapters 1 and 2.
The timetable and the Deccan Rail passenger guide are invented for the book.

1. Make sure the Ollama app is running.
2. Open Command Prompt and go to this folder:
       cd %USERPROFILE%\Desktop\Preparation\Book_Proposal\code\chapter3
3. Activate the book's environment:
       ..\chapter1\.venv312\Scripts\activate
4. Quick check (about 8 minutes):
       python run_all.py --quick
5. Full experiment (about 40 minutes):
       python run_all.py
   When it says "All done", tell Claude.

Files
-----
workflow3.py    Listing 3-1  the same job as a CrewAI Flow (a workflow)
knowledge3.py   Listing 3-2  retrieval from the passenger guide, as a tool
memory3.py      Listing 3-3  long-term memory of traveller preferences
designs3.py     Listing 3-4  all the designs compared in the chapter
agents3.py      Listing 3-5  the repaired checker (criteria, evidence, default)
guardrail3.py   Listing 3-6  guardrail that also checks the time of day
requests.json, policy_questions.json, memory_requests.json   test sets
runner3.py, run_all.py, lib\   experiment scripts (not printed in the book)
