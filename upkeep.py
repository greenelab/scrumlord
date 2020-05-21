import argparse
import datetime
import functools
import re
import sys
import traceback
import typing

import holidays
import github


class PennHolidays(holidays.UnitedStates):

    def _populate(self, year):
        super()._populate(year)

        # See https://github.com/greenelab/scrum/issues/114
        for day in range(26, 32):
            self[datetime.date(year, 12, day)] = 'Special Winter Vacation'


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


def get_today() -> datetime.date:
    """
    Returns the datetime.date for today. Needed since tests cannot mock a
    builtin type: http://stackoverflow.com/a/24005764/4651668
    """
    return datetime.date.today()


def is_holiday(date: datetime.date) -> bool:
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


@functools.lru_cache()
def issue_title_to_date(title: str) -> typing.Optional[datetime.date]:
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
        if issue.state == 'closed':
            continue
        title = issue.title
        date = issue_title_to_date(title)
        if not date:
            continue
        if today - date > lifespan:
            print('Closing', title, file=sys.stderr)
            try:
                issue.edit(state='closed')
            except Exception:
                print('Closing issue failed:\n{}'.format(traceback.format_exc()), file=sys.stderr)


def create_scrum_issue(
        repo: github.Repository.Repository,
        date: datetime.date,
        previous_issue: github.Issue.Issue = None,
    ) -> typing.Optional[github.Issue.Issue]:
    """
    Create a scrum issue for the given date.
    If not None, previous_issue is used to set an issue body
    that refers to the previous issue.
    """
    kwargs = {'title': f"{date}: e-scrum for {date:%A, %B %-d, %Y}"}
    if previous_issue:
        kwargs['body'] = 'Preceeding e-scrum in {}.'.format(previous_issue.html_url)
    print('Creating {title!r}'.format(**kwargs), file=sys.stderr)
    try:
        return repo.create_issue(**kwargs)
    except Exception:
        print('Creating issue failed:\n{}'.fomrat(traceback.format_exc()), file=sys.stderr)


def get_future_dates_without_issues(issues, workdays_ahead: int = 2):
    """
    Look through issues and yield the dates of future workdays (includes today)
    that don't have open issues.
    """
    future_dates = set(get_upcoming_workdays(workdays_ahead))
    future_dates -= {issue_title_to_date(x.title) for x in issues}
    return sorted(future_dates)


def get_upcoming_workdays(workdays_ahead: int = 2) -> typing.Iterator[datetime.date]:
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
    parser.add_argument('--username', default='scrum-lord')
    parser.add_argument(
        '--token', help='GitHub personal access token for --username')
    parser.add_argument('--repository', default='greenelab/scrum')
    parser.add_argument('--lifespan', type=int, default=7)
    parser.add_argument('--workdays-ahead', type=int, default=2)
    args = parser.parse_args()

    gh = github.Github(args.username, args.token)
    user = gh.get_user()

    # Get greenelab/scrum repository. Could not find a better way
    repo, = [
        repo for repo in user.get_repos()
        if repo.full_name == args.repository
    ]

    # Get open issues
    open_issues = list(repo.get_issues(state='open'))

    # Close old issues
    close_old_issues(open_issues, args.lifespan)

    # Get n most recent issues (open or closed), where n = 10 + --workdays-ahead
    # to help ensure the most recent existing e-scrum issue is included even when other
    # non e-scrum issues exist
    issues = repo.get_issues(state='all', sort='number', direction='desc')
    issues = issues[:min(10 + args.workdays_ahead, issues.totalCount)]
    date_issue_pairs = [(issue_title_to_date(issue.title), issue) for issue in issues]
    # Filter issues that are not scrum entries
    date_issue_pairs = sorted((date, issue) for date, issue in date_issue_pairs if date)

    # Detect previous issue for creation of the first upcoming issue
    previous_issue = None
    if date_issue_pairs:
        _, previous_issue = date_issue_pairs[-1]

    # Create upcoming issues
    dates = get_future_dates_without_issues(issues, args.workdays_ahead)
    for date in dates:
        previous_issue = create_scrum_issue(repo, date, previous_issue)
