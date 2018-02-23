import argparse
import datetime
import re

import holidays
import github


class PennHolidays(holidays.UnitedStates):

    def _populate(self, year):
        super()._populate(year)


holiday_names = {
    'Independence Day',
    'Labor Day',
    'Thanksgiving',
    'Christmas Day',
    "New Year's Day",
    'Martin Luther King, Jr. Day',
    'Memorial Day',
    'Special Winter Vacation',
}

penn_holidays = PennHolidays()


def get_today():
    """
    Returns the datetime.date for today. Needed since tests cannot mock a
    builtin type: http://stackoverflow.com/a/24005764/4651668
    """
    return datetime.date.today()


def is_holiday(date) -> bool:
    """
    Return True or False for whether a date is a holiday
    """
    name = penn_holidays.get(date)
    if not name:
        return False
    name = name.replace(' (Observed)', '')
    return name in holiday_names


def is_workday(date) -> bool:
    """
    Return boolean for whether a date is a workday.
    """
    if date.weekday() in holidays.WEEKEND:
        return False
    if is_holiday(date):
        return False
    return True


def issue_title_to_date(title: str):
    """
    Return a datetime.date object from a Scrum issue title.
    """
    pattern = re.compile(r'([0-9]{4})-([0-9]{2})-([0-9]{2}):')
    match = pattern.match(title)
    if not match:
        return None
    return datetime.date(*map(int, match.groups()))


def close_old_issues(issues, lifespan: int):
    """
    Close scrum issues older than the number of days specified by lifespan.
    """
    lifespan = datetime.timedelta(days=lifespan)
    today = get_today()
    for issue in issues:
        title = issue.title
        date = issue_title_to_date(title)
        if not date:
            continue
        if today - date > lifespan:
            print('Closing', title)
            try:
                issue.edit(state='closed')
            except Exception as e:
                print('Closing issue failed:', e)


def create_scrum_issue(repo, date):
    """
    Create a scrum issue for the given date
    """
    title = f"{date}: e-scrum for {date:%A, %B %-d, %Y}"
    print('Creating', title)
    try:
        repo.create_issue(title)
    except Exception as e:
        print('Creating issue failed:', e)


def get_future_dates_without_issues(issues, workdays_ahead=2):
    """
    Look through issues and yield the dates of future workdays (includes today)
    that don't have open issues.
    """
    future_dates = set(get_upcoming_workdays(workdays_ahead))
    future_dates -= {issue_title_to_date(x.title) for x in issues}
    return sorted(future_dates)


def get_upcoming_workdays(workdays_ahead=2):
    """
    Return a generator of the next number of workdays specified by
    workdays_ahead. The current day is yielded first, if a workday,
    and does not count as one of workdays_ahead.
    """
    date = get_today()
    if is_workday(date):
        yield date
    i = 0
    while i < workdays_ahead:
        date += datetime.timedelta(days=1)
        if is_workday(date):
            yield date
            i += 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--username', default='kurtwheeler')
    parser.add_argument(
        '--token', help='GitHub personal access token for --username')
    parser.add_argument('--repository', default='alexslemonade/scrum')
    parser.add_argument('--lifespan', type=int, default=7)
    parser.add_argument('--workdays-ahead', type=int, default=2)
    args = parser.parse_args()

    gh = github.Github(args.username, args.token)
    user = gh.get_user()

    # Get Alexsleomonade/scrum repository. Could not find a better way
    repo, = [repo for repo in user.get_repos()
             if repo.full_name == args.repository]

    # Get open issues
    issues = list(repo.get_issues())

    # Close old issues
    close_old_issues(issues, args.lifespan)

    # Create upcoming issues
    dates = get_future_dates_without_issues(issues, args.workdays_ahead)
    for date in dates:
        create_scrum_issue(repo, date)
