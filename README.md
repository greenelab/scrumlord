# Greene Lab Electronic Scrum

[![Build Status](https://travis-ci.com/greenelab/scrum.svg?token=7FyZyp7bN9WxFnsviy1B&branch=master)](https://travis-ci.com/greenelab/scrum)

This repository is home to the Greene Lab's electronic [scrum](http://greenelab-onboarding.readthedocs.io/en/latest/communication.html?highlight=scrum) (e-scrum).
Scrums occur via [issues](https://github.com/greenelab/scrum/issues) using GitHub flavored markdown and its [task lists interface](https://github.com/blog/1375-task-lists-in-gfm-issues-pulls-comments).

The [**@scrum-lord**](https://github.com/scrum-lord) is a machine user who maintains the issues via daily Travis CI cron jobs.

## GitHub Email Notifications

Users may want to adjust their notification preferences so they receive emails only when they're mentioned and not when they participate in an issue.
This is not an option provided by GitHub, so the following workaround is recommended:

1. Set your `greenelab/scrum` [notification status](https://github.com/greenelab/scrum/subscription) to **Not Watching**,
  so "you will only receive notifications when you participate or are `@mentioned`."

2. Create an email filter to delete messages sent to `scrum@noreply.github.com` that contain the text "You are receiving this because you commented."
  In Gmail, the filter syntax looks like:

  ```
  to:(scrum@noreply.github.com) "You are receiving this because you commented."
  ```

With the above policy, you will still receive notifications where:
"You are receiving this because you were mentioned."
