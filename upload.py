#!/usr/bin/env python3
import os

from dotenv import load_dotenv
from mwapi import Session


def read_chunks(file_object, chunk_size):
    while data := file_object.read(chunk_size):
        aligned = len(data) == chunk_size
        yield data
    if aligned:
        # yield a final empty chunk to signal end-of-file,
        # so that we still send an action=upload request where
        # filesize == offset + len(chunk)
        yield ''


def upload(session, file_object, file_name, wikitext, comment):
    chunk_size = 1024 * 1024
    chunks = read_chunks(file_object, chunk_size)
    token = session.get(action='query',
                        meta='tokens')['query']['tokens']['csrftoken']
    offset = 0
    file_key = None

    for chunk in chunks:
        params = {
            'action': 'upload',
            'stash': '1',
            'filename': file_name,
            'offset': offset,
            'token': token,
            'upload_file': chunk,
        }
        if file_key:
            params['filekey'] = file_key
        if len(chunk) < chunk_size:
            # this is the last chunk
            params['filesize'] = offset + len(chunk)
        else:
            # we don’t know the filesize,
            # so so just say “we’re not done yet”
            params['filesize'] = offset + len(chunk) + 1
        response = session.post(**params)
        offset = response['upload']['offset']
        file_key = response['upload']['filekey']

    session.post(action='upload',
                 filename=file_name,
                 filekey=file_key,
                 token=token,
                 comment=comment,
                 text=wikitext)


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
    # TODO everything else :)


if __name__ == '__main__':
    main()
