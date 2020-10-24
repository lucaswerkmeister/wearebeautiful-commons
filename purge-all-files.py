#!/usr/bin/env python3

import time

import mwapi

session = mwapi.Session(
    host='https://commons.wikimedia.org',
    user_agent='We Are Beautiful purger (mail@lucaswerkmeister.de)',
)

for result in session.post(
        action='purge',
        generator='categorymembers',
        gcmtitle='Category:We Are Beautiful',
        gcmtype='file',
        gcmlimit=30,  # rate limit permits 30 purges per 60 seconds
        forcelinkupdate=True,
        continuation=True,
    ):
    pages = result['purge']
    first_title = pages[0]['title']
    last_title = pages[-1]['title']
    print('Purged {}\nUntil  {}'.format(first_title, last_title), flush=True)
    time.sleep(75)  # rate limit permits 30 purges per 60 seconds, +15s for some buffer

print('Done.')
