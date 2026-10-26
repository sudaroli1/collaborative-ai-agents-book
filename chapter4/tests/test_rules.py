"""Listing 4-7. Unit tests: fast, free and exact, because no model runs."""
from rules4 import choose_train
from rail_tools import search_trains

SAT = search_trains.run(origin="Bengaluru", destination="Mysuru",
                        day="Saturday").splitlines()


def test_first_morning_train_with_window():
    assert choose_train(SAT, "morning", window=True) == "16017"


def test_morning_without_window_takes_first_train():
    assert choose_train(SAT, "morning") == "16001"


def test_no_afternoon_train():
    assert choose_train(SAT, "afternoon") == "NONE"


def test_unknown_route_gives_none():
    lines = search_trains.run(origin="Chennai", destination="Mysuru",
                              day="Saturday").splitlines()
    assert choose_train(lines) == "NONE"


def test_tool_is_case_insensitive():
    assert search_trains.run(origin="bengaluru", destination="MYSURU",
                             day="saturday").splitlines() == SAT
