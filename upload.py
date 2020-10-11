#!/usr/bin/env python3
import os

from dotenv import load_dotenv
from mwapi import Session

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
