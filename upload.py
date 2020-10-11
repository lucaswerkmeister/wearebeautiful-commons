#!/usr/bin/env python3
import gzip
import os
import sys

from dotenv import load_dotenv
from mwapi import Session

from wikitext import load_data, data_to_page_wikitext, data_to_description


bot_url = 'https://github.com/lucaswerkmeister/wearebeautiful-commons'


def csrf_token(session):
    if not hasattr(session, 'csrf_token'):
        response = session.get(action='query',
                               meta='tokens')
        session.csrf_token = response['query']['tokens']['csrftoken']
    return session.csrf_token


def upload(session, file_object, file_name, wikitext, comment):
    token = csrf_token(session)

    response = session.post(action='upload',
                            filename=file_name,
                            upload_file=file_object,
                            token=token,
                            comment=comment,
                            text=wikitext)

    assert response['upload']['result'] == 'Success', response


def add_caption(session, file_name, caption):
    response = session.get(action='query',
                           titles=f'File:{file_name}',
                           formatversion=2)
    page_id = response['query']['pages'][0]['pageid']
    entity_id = f'M{page_id}'
    session.post(action='wbsetlabel',
                 id=entity_id,
                 language='en',
                 value=caption,
                 summary=f'via {bot_url}',
                 token=csrf_token(session))


def load_and_upload(session, manifest_file):
    data = load_data(manifest_file)
    model_code = data['model_code']
    for stl_type in ('surface', 'solid'):
        file_name = f'We Are Beautiful – {model_code} – {stl_type}.stl'
        wikitext = data_to_page_wikitext(data, stl_type)
        description = data_to_description(data, stl_type)
        comment = f'Upload via {bot_url}'
        stl_path = manifest_file.replace('-manifest.json',
                                         f'-{stl_type}.stl.gz')
        with gzip.open(stl_path, 'rb') as stl_file:
            upload(session, stl_file, file_name, wikitext, comment)
        add_caption(session, file_name, description)


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

    for manifest_file in sys.argv[1:]:
        load_and_upload(session, manifest_file)


if __name__ == '__main__':
    main()
