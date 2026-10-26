"""Makes the pilot test set: 36 return-trip requests written in the
varied ways real travellers write, with the correct answers worked out
by the booking rules (Listing 4-3). Run once; writes pilot_requests.json."""
import json, random, sys
from pathlib import Path
HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "chapter4"))
from rail_tools import search_trains
from rules4 import choose_train

random.seed(5)
NAMES = {"Bengaluru": ["Bengaluru", "Bangalore", "B'lore"],
         "Mysuru": ["Mysuru", "Mysore"]}
WHEN = {"morning": ["morning", "in the morning", "before noon"],
        "afternoon": ["afternoon", "after lunch"],
        "evening": ["evening", "in the evening"],
        "": [""]}
WINDOW = [(True, "window seat please"), (True, "I need a window seat"),
          (True, "by the window"), (False, ""), (False, "any seat")]
FORMS = ["{o} to {d} on {day1} {t1}, back on {day2} {t2}. {w}",
         "I want to travel from {o} to {d} on {day1} {t1} and return on "
         "{day2} {t2}. {w}",
         "Need trains {o}-{d} {day1} {t1}, return {day2} {t2}, {w}",
         "Book a return trip: {day1} {t1} {o} to {d}, coming back {day2} "
         "{t2}. {w}"]
PLANS = [("Saturday", "Sunday"), ("Saturday", "Saturday"),
         ("Sunday", "Sunday")]

rows = []
for i in range(36):
    day1, day2 = random.choice(PLANS)
    t1 = random.choice(["morning", "afternoon", "evening"])
    t2 = random.choice(["afternoon", "evening", ""])
    if day1 == day2 and t2 == "":
        t2 = "evening"
    win, wtext = random.choice(WINDOW)
    old = random.random() < 0.3              # about one in three
    o = random.choice(NAMES["Bengaluru"][1:]) if old else "Bengaluru"
    d = random.choice(NAMES["Mysuru"][1:]) if old else "Mysuru"
    text = random.choice(FORMS).format(
        o=o, d=d, day1=day1, day2=day2, w=wtext.capitalize(),
        t1=random.choice(WHEN[t1]), t2=random.choice(WHEN[t2]))
    text = " ".join(text.replace(" .", ".").replace(" ,", ",").split())
    out = choose_train(search_trains.run(origin="Bengaluru",
                       destination="Mysuru", day=day1).splitlines(), t1, win)
    ret = choose_train(search_trains.run(origin="Mysuru",
                       destination="Bengaluru", day=day2).splitlines(), t2,
                       win)
    rows.append({"id": f"R{i + 1:02d}", "text": text, "outbound": out,
                 "return": ret, "old_names": old, "window": win})
json.dump(rows, open(HERE / "pilot_requests.json", "w"), indent=1)
print(len(rows), "requests;", sum(r["old_names"] for r in rows),
      "use old city names")
