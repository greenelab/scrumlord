import argparse
import datetime
import re

import holidays
import github

penn_holidays = {
    'Independence Day',
    'Labor Day',
    'Thanksgiving',
    'Christmas Day',
    "New Year's Day",
    'Martin Luther King, Jr. Day',
    'Memorial Day',
}

us_holidays = holidays.UnitedStates()


def is_holiday(date) -> bool:
    """
    Return True or False for whether a date is a holiday
    """
    name = us_holidays.get(date)
    if not name:
        return False
    name = name.replace(' (Observed)', '')
    return name in penn_holidays


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
    today = datetime.date.today()
    for issue in issues:
        title = issue.title
        date = issue_title_to_date(title)
        if not date:
            continue
        if today - date > lifespan:
            print('Closing', title)
            issue.edit(state='closed')


def create_scrum_issue(repo, date):
    """
    Create a scrum issue for the given date
    """
    title = f"{date}: e-scrum for {date:%A, %B %-d, %Y}"
    print('Creating', title)
    repo.create_issue(title)


def get_future_dates_without_issues(issues, days_ahead=2):
    """
    Look through issues and yield future dates that don't exist.
    """
    dates = {issue_title_to_date(x.title) for x in issues}
    today = datetime.date.today()
    for i in range(days_ahead + 1):
        date = today + datetime.timedelta(days=i)
        if date not in dates and is_workday(date):
            yield date
            dates.add(date)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--username', default='scrum-lord')
    parser.add_argument('--token')
    parser.add_argument('--lifespan', type=int, default=7)
    args = parser.parse_args()

    gh = github.Github(args.username, args.token)
    user = gh.get_user()

    # Get greenelab/scrum repository. Could not find a better way
    repo, = [repo for repo in user.get_repos()
             if repo.full_name == 'greenelab/scrum']

    # Get open issues
    issues = list(repo.get_issues())

    # Close old issues
    close_old_issues(issues, args.lifespan)

    # Create upcoming issues
    for date in get_future_dates_without_issues(issues):
        create_scrum_issue(repo, date)
