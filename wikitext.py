#!/usr/bin/env python3
import json
import re
import sys

body_part_lookup = {
    'A': 'anatomical',
    'F': 'full body',
    'L': 'lower body',
    'U': 'upper body',
    'B': 'breast',
    'O': 'buttocks',
    'N': 'nipple',
    'P': 'penis',
    'T': 'torso',
    'V': 'vulva',
    'H': 'hand',  # not documented on https://wearebeautiful.info/docs/model-codes
}
pose_lookup = {
    'S': 'standing',
    'T': 'sitting',
    'L': 'lying',
    'U': 'lying, legs pulled up',
}
arrangement_lookup = {
    'S': 'spread',
    'R': 'retracted',
    'A': 'arranged',
    'N': 'natural',
}
excited_lookup = {
    'N': 'not excited',
    'X': 'excited',
    'P': 'partially excited',
}

def load_to_wikitext(file_name):
    (human_model,
     body_part, pose, arrangement, excited,
     model_code) = \
         re.match(r'(?:\./)?wearebeautiful-models/([^/]*)/(.)(.)(.)(.)/(.*)-manifest.json',
                  file_name).groups()

    body_part = body_part_lookup[body_part]
    pose = pose_lookup[pose]
    arrangement = arrangement_lookup[arrangement]
    excited = excited_lookup[excited]

    with open(file_name) as f:
        data = json.load(f)

    assert arrangement == data['arrangement']
    assert body_part == data['body_part']
    body_type = data['body_type']
    comment = data.get('comment')
    created = data['created']
    assert excited == data['excited']
    gender = data['gender']
    gender_comment = data.get('gender_comment')
    given_birth = data['given_birth']
    history = data.get('history', [])  # TODO unused
    assert human_model == data['id']
    # TODO links
    # make_solid_args ignored
    # other currently always {}
    assert pose == data['pose']
    released = data['released']
    sex = data['sex']
    sex_comment = data.get('sex_comment')
    tags = data.get('tags', [])  # TODO unused
    version = data['version']

    wikitext = f'''{{{{We Are Beautiful model
|model_code={model_code}
|human_model={human_model}
|body_part={body_part}
|pose={pose}
|arrangement={arrangement}
|excited={excited}
|version={version}
|body_type={body_type}'''
    if comment:
        wikitext += f'\n|comment={comment}'
    wikitext += f'''
|created={created}
|gender={gender}'''
    if gender_comment:
        wikitext += f'\n|gender_comment={gender_comment}'
    wikitext += f'''
|given_birth={given_birth}
|released={released}
|sex={sex}'''
    if sex_comment:
        wikitext += f'\n|sex_comment={sex_comment}'
    wikitext += '''
|stl_type=REPLACEME
}}'''

    return wikitext

for file_name in sys.argv[1:]:
    print(load_to_wikitext(file_name))
