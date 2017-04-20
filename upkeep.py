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


def close_old_issues(repo, lifespan: int):
    """
    Close scrum issues older than the number of days specified by lifespan.
    """
    lifespan = datetime.timedelta(lifespan)
    today = datetime.date.today()
    for issue in repo.get_issues():
        title = issue.title
        date = issue_title_to_date(title)
        if not date:
            continue
        if today - date > lifespan:
            print('Closing', title)
            issue.edit(state='closed')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--username', default='scrum-lord')
    parser.add_argument('--token')
    parser.add_argument('--lifespan', type=int, default=7)
    args = parser.parse_args()

    gh = github.Github(args.username, args.token)
    user = gh.get_user()

    # Get greenelab/scrum repository. Could not find a better way
    for repo in user.get_repos():
        if repo.full_name == 'greenelab/scrum':
            break

    close_old_issues(repo, args.lifespan)
