CHAPTER 1 CODE - HOW TO RUN (Windows, about 5 minutes of your time)
=====================================================================
The timetable in data/timetable.csv is invented for the book.

1. Make sure the Ollama app is running (its icon is in the taskbar).

2. Open Command Prompt and download the model (once, about 5 GB):
       ollama pull llama3.1:8b

3. Go to this folder:
       cd %USERPROFILE%\Desktop\Preparation\Book_Proposal\code\chapter1

4. Create a clean Python environment for the book (once).
   CrewAI 1.15 needs Python 3.10-3.13. The uv tool fetches a suitable Python:
       python -m pip install uv
       python -m uv venv .venv312 --python 3.12
       .venv312\Scripts\activate
       python -m uv pip install -r requirements.txt
   (Next time, just run  .venv312\Scripts\activate  before step 5.)

5. Run all Chapter 1 experiments:
       python run_all.py

   It prints progress lines such as "[B] agent run 2/3: R2_sunday".
   On a laptop without a graphics card it can take 20-40 minutes.
   For a quick test first:  python run_all.py --repeats 1

6. When it says "All done", tell Claude. The results are saved in the
   "results" folder and will be inserted into Section 1.4.

Files
-----
listing_1_1_chatbot.py      Listing 1-1  bare language model
rail_tools.py               Listing 1-2  the search_trains tool
listing_1_3_first_agent.py  Listings 1-3 and 1-4  the agent, task and crew
agent_runner.py, run_all.py experiment scripts (not printed in the book)
