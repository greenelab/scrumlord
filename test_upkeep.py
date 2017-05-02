import datetime

import pytest

import upkeep


class Issue:
    """
    Mock of github.Issue.Issue class
    """
    def __init__(self, title):
        self.title = title


@pytest.mark.parametrize("date_tuple,holiday", [
    ((2016, 12, 27), True),  # Special Winter Vacation
    ((2016, 12, 28), True),  # Special Winter Vacation
    ((2016, 12, 29), True),  # Special Winter Vacation
    ((2016, 12, 30), True),  # Special Winter Vacation
    ((2016, 12, 31), True),  # Special Winter Vacation
    ((2016, 7, 4), True),  # Independence Day
    ((2017, 7, 4), True),  # Independence Day
    ((2017, 1, 2), True),  # New Year’s Day
    ((2017, 1, 3), False),
    ((2015, 1, 10), False),
    ((2019, 5, 27), True),  # Memorial Day
])
def test_is_holiday(date_tuple, holiday):
    date = datetime.date(*date_tuple)
    assert upkeep.is_holiday(date) == holiday


@pytest.mark.parametrize("date_tuple,workday", [
    ((2017, 1, 2), False),  # New Year’s Day
    ((2017, 4, 17), True),  # Monday
    ((2017, 4, 18), True),  # Tuesday
    ((2017, 4, 19), True),  # Wednesday
    ((2017, 4, 20), True),  # Thursday
    ((2017, 4, 21), True),  # Friday
    ((2017, 4, 22), False),  # Saturday
    ((2017, 4, 23), False),  # Sunday
])
def test_is_workday(date_tuple, workday):
    date = datetime.date(*date_tuple)
    assert upkeep.is_workday(date) == workday


@pytest.mark.parametrize("title,date_tuple", [
    ('2017-04-21: e-scrum for Friday, April 21, 2017', (2017, 4, 21)),
    ('2017-04-11: e-scrum for Tuesday, April 11, 2017', (2017, 4, 11)),
    ('2016-11-08: e-scrum for Tuesday, November 8, 2016', (2016, 11, 8)),
    ('This is an issue from 2016-11-08, not a scrum', None),
])
def test_issue_title_to_date(title, date_tuple):
    date = datetime.date(*date_tuple) if date_tuple else None
    assert upkeep.issue_title_to_date(title) == date


def test_get_future_dates_without_issues_friday(monkeypatch):
    today = datetime.date(2017, 4, 21)  # Friday
    monkeypatch.setattr('upkeep.get_today', lambda: today)
    expected = [
        datetime.date(2017, 4, 21),  # Friday, today
        datetime.date(2017, 4, 24),  # Monday
        datetime.date(2017, 4, 25),  # Tuesday
        datetime.date(2017, 4, 26),  # Wednesday
    ]
    issues = []  # No open issues
    dates = upkeep.get_future_dates_without_issues(issues, workdays_ahead=3)
    assert list(dates) == expected


def test_get_future_dates_without_issues_saturday(monkeypatch):
    today = datetime.date(2017, 4, 22)  # Saturday
    monkeypatch.setattr('upkeep.get_today', lambda: today)
    expected = [
        datetime.date(2017, 4, 24),  # Monday
        datetime.date(2017, 4, 25),  # Tuesday
    ]
    issues = []  # No open issues
    dates = upkeep.get_future_dates_without_issues(issues, workdays_ahead=2)
    assert list(dates) == expected


def test_get_future_dates_without_issues_monday(monkeypatch):
    today = datetime.date(2017, 4, 24)  # Monday
    monkeypatch.setattr('upkeep.get_today', lambda: today)
    expected = [
        datetime.date(2017, 4, 24),  # Monday
        datetime.date(2017, 4, 25),  # Tuesday
        datetime.date(2017, 4, 26),  # Wednesday
    ]
    issues = []  # No open issues
    dates = upkeep.get_future_dates_without_issues(issues, workdays_ahead=2)
    assert list(dates) == expected


def test_get_future_dates_without_issues_wednesday(monkeypatch):
    """
    Issue already open for current workday.
    """
    issues = [
        Issue('2017-04-26: e-scrum for Wednesday, April 26, 2017'),
    ]
    today = datetime.date(2017, 4, 26)  # Wednesday
    monkeypatch.setattr('upkeep.get_today', lambda: today)
    expected = [
        datetime.date(2017, 4, 27),  # Thursday
        datetime.date(2017, 4, 28),  # Friday
    ]
    dates = upkeep.get_future_dates_without_issues(issues, workdays_ahead=2)
    assert list(dates) == expected
