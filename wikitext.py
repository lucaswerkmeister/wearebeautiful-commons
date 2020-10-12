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


def load_data(file_name):
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
    assert excited == data['excited']
    assert human_model == data['id']
    assert pose == data['pose']

    data['model_code'] = model_code

    return data


def data_to_template_wikitext(data, stl_type='REPLACEME'):
    arrangement = data['arrangement']
    body_part = data['body_part']
    body_type = data['body_type']
    comment = data.get('comment')
    created = data['created']
    excited = data['excited']
    gender = data['gender']
    gender_comment = data.get('gender_comment')
    given_birth = data['given_birth']
    history = data.get('history', [])  # TODO unused
    human_model = data['id']
    # TODO links
    # make_solid_args ignored
    model_code = data['model_code']
    # other currently always {}
    pose = data['pose']
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
    wikitext += f'''
|stl_type={stl_type}
}}}}'''

    return wikitext


def data_to_description(data, stl_type='REPLACEME'):
    # based on https://github.com/wearebeautiful/wearebeautiful-web/blob/a5ad23c49a790fcd01f1dd47a62f89a43e7ae15d/web/wearebeautiful/db_model.py#L59
    description = f'a {data["body_part"]} model of '
    if data['sex'] in ('male', 'female'):
        description += 'a ' + data['sex']
    elif data['sex'] == 'intersex':
        description += 'an intersex pesrson'
    else:
        description += 'a person'

    description += f' who is {data["pose"]}'
    if data['pose'] == 'lying':
        description += ' down'

    if data['given_birth'] != 'no':
        description += f' and has given {data["given_birth"]} birth'

    description += f' ({stl_type} version)'

    return description


def data_to_categories(data):
    '''Guess some categories for the data.

    This need not be perfect, and editors may adjust the categories
    later. It’s only meant as a first version, better than nothing.'''
    categories = []

    body_part = data['body_part']
    sex = data['sex']
    if body_part == 'full body':
        categories.append({
            'male': 'Human male body',
            'female': 'Human female body',
        }.get(sex, 'Human body'))
    elif body_part == 'breast':
        categories.append({
            'male': 'Male human breasts',
            'female': 'Female human breasts',
        }.get(sex, 'Human breasts'))
    elif body_part == 'buttocks':
        categories.append({
            'male': 'Male buttocks',
            'female': 'Female buttocks',
        }.get(sex, 'Human buttocks'))
    elif body_part == 'nipple':
        categories.append({
            'male': 'Male nipples',
            'female': 'Female nipples',
        }.get(sex, 'Human nipples'))
    elif body_part == 'penis':
        categories.append({
            'not excited': 'Flaccid human penis',
            'excited': 'Erect human penis',
            'partially excited': 'Semi-erect human penis',
        }[data['excited']])
    elif body_part == 'torso':
        categories.append({
            'male': 'Male human torsos',
            'female': 'Female human torsos',
        }.get(sex, 'Human torsos'))
    elif body_part == 'vulva':
        categories.append('Human vulvas')
    elif body_part == 'hand':
        categories.append({
            'male': 'Male hands',
            'female': 'Female hands',
        }.get(sex, 'Human hands'))

    categories.append('STL body parts')

    return categories


def data_to_page_wikitext(data, stl_type='REPLACEME'):
    template_wikitext = data_to_template_wikitext(data, stl_type=stl_type)
    description = data_to_description(data, stl_type=stl_type)
    categories = data_to_categories(data)
    categories_wikitext = '\n'.join(f'[[Category:{category}]]'
                                    for category in categories)
    model_code = data['model_code']
    date = data['released']
    source = f'https://wearebeautiful.info/model/{model_code}'

    return f'''=={{{{int:filedesc}}}}==
{{{{Information
|description={{{{en|1={description}}}}}
|date={date}
|source={source}
|author=We Are Beautiful
}}}}

=={{{{int:license-header}}}}==

{template_wikitext}
{{{{3dpatent}}}}

{categories_wikitext}'''


if __name__ == '__main__':
    for file_name in sys.argv[1:]:
        print(data_to_page_wikitext(load_data(file_name)))
