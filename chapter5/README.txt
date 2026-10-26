CHAPTER 5 CODE - HOW TO RUN
===========================
Needs the Chapter 4 folder next to this one (it reuses Listing 4-4), the
book's Python environment, and both models (llama3.1:8b, llama3.2:3b).

  1. Make sure the Ollama app is running.
  2. cd %USERPROFILE%\Desktop\Preparation\Book_Proposal\code\chapter5
  3. ..\chapter1\.venv312\Scripts\activate
  4. Quick check (about 3 minutes):   python run_all.py --quick
  5. Full pilot (about 30 minutes):   python run_all.py
     When it says "All done", tell Claude.

Files
-----
pilot5.py          Listing 5-1  the pilot measurement
make_requests5.py  makes the 36 varied requests and their correct answers
run_all.py, runner_util.py      helper scripts (not printed)
