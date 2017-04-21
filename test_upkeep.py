import datetime

import pytest

import upkeep


@pytest.mark.parametrize("date_tuple,holiday", [
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
