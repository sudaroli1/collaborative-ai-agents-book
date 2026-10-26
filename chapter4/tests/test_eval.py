"""Listing 4-8. The evaluation set as a test: slow, and judged by a
threshold, because the model is not exact. Run: pytest -m llm"""
import json, os, re
from pathlib import Path
import pytest
from workflow4 import TripWorkflow

TRIPS = json.loads((Path(__file__).parent.parent / "trips.json")
                   .read_text(encoding="utf-8"))
MIN_CORRECT = 5                       # of 6: the bar for a release
results = []


def plan(text):
    answer = str(TripWorkflow().kickoff(inputs={"request": text}))
    get = lambda k: re.findall(k + r": (\d{5}|NONE)", answer)[-1:]
    return (get("OUTBOUND") or ["?"])[0], (get("RETURN") or ["?"])[0]


@pytest.mark.llm
@pytest.mark.parametrize("trip", TRIPS, ids=[t["id"] for t in TRIPS])
def test_trip(trip):
    out, ret = plan(trip["text"])
    results.append(out in trip["outbound"] and ret in trip["return"])
    print(trip["id"], out, ret)


@pytest.mark.llm
def test_release_bar():                  # runs after the six trips
    print(f"{sum(results)} of {len(results)} trips correct "
          f"with {os.environ.get('BOOK_MODEL', 'llama3.1:8b')}")
    assert sum(results) >= MIN_CORRECT
