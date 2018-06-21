# Continuous administration of the Greene Lab's electronic scrum

[![Build Status](https://travis-ci.org/greenelab/scrumlord.svg?branch=master)](https://travis-ci.org/greenelab/scrumlord)

## Summary

This repository automates the management of GitHub issues, which must be opened and closed based on the date.

## Details

The Greene Lab does an electronic [scrum](http://greenelab-onboarding.readthedocs.io/en/latest/communication.html?highlight=scrum) (e-scrum) where lab members create daily task lists using GitHub issues on [`greenelab/scrum`](https://github.com/greenelab/scrum) (private repository).
To automate the administration of `greenelab/scrum` issues, this repository relies on Travis CI daily cron jobs and a GitHub machine user named [**@scrum-lord**](https://github.com/scrum-lord).
Every day, Travis CI executes the commands in [`.travis.yml`](.travis.yml).
As appropriate, **@scrum-lord** closes and opens issues to keep the scrum issues up to date.

## Deployment Instructions

Use these instructions to deploy a new instance of the scrumlord to manage scrum issues for a repository

1. Fork repo
2. Create new empty repo organization/scrum
3. Get Github login token (https://help.github.com/articles/creating-a-personal-access-token-for-the-command-line/) with repo scope
   - The safest way to do this is to create a new machine user that doesn't have any other privileges than for the scrum repo
4. log into https://travis-ci.com using github
5. Add new repo to travis-ci: organization/scrumlord
6. In the settings for that travis-ci repo:
   - Add daily [cronjob](https://docs.travis-ci.com/user/cron-jobs/) to always run master branch
   - Create environment variable named `GH_TOKEN` whose value is the login token from step 3.
7. Commit changes to master branch to fit your settings (see https://github.com/gentnerlab/scrumlord/network for examples)

## Reuse

Anyone is welcome to adapt this codebase for their use cases.
The repository is openly licensed as per [`LICENSE.md`](LICENSE.md).
