#!/usr/bin/env python3
import os
import re
import sys

from dotenv import load_dotenv
from mwapi import Session


bot_url = 'https://github.com/lucaswerkmeister/wearebeautiful-commons'


def csrf_token(session):
    if not hasattr(session, 'csrf_token'):
        response = session.get(action='query',
                               meta='tokens')
        session.csrf_token = response['query']['tokens']['csrftoken']
    return session.csrf_token


def create(session, human_model):
    token = csrf_token(session)

    title = f'Category:We Are Beautiful human model {human_model}'
    text = f'''
[[Category:We Are Beautiful by human model|{human_model}]]
'''.strip()
    comment = f'Upload via {bot_url}'

    response = session.post(action='edit',
                            title=title,
                            text=text,
                            summary=comment,
                            token=token,
                            contentformat='text/x-wiki',
                            contentmodel='wikitext')

    assert response['edit']['result'] == 'Success', response


def main():
    load_dotenv()

    username = os.getenv('MW_USERNAME')
    password = os.getenv('MW_PASSWORD')
    if not username or not password:
        raise Exception('Username or password not provided!')

    user_agent = 'We Are Beautiful upload (mail@lucaswerkmeister.de)'
    session = Session('https://commons.wikimedia.org',
                      user_agent=user_agent)
    lgtoken = session.get(action='query',
                          meta='tokens',
                          type='login')['query']['tokens']['logintoken']
    session.post(action='login',
                 lgname=username,
                 lgpassword=password,
                 lgtoken=lgtoken)

    for directory in sys.argv[1:]:
        human_model = re.match(r'(?:\./)?(?:wearebeautiful-models/)?([^/]*).*',
                               directory).groups()[0]
        print(f'Creating {human_model}...')
        create(session, human_model)


if __name__ == '__main__':
    main()
