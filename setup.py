from setuptools import setup
import sys
import json


with open('metadata.json', encoding='utf-8') as fp:
    metadata = json.load(fp)


setup(
    name='lexibank_iecor',
    description=metadata['title'],
    license=metadata.get('license', ''),
    url=metadata.get('url', ''),
    py_modules=['lexibank_iecor'],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'lexibank.dataset': [
            'iecor=lexibank_iecor:Dataset',
        ]
    },
    install_requires=[
        'pylexibank>=2.1', 'pycdstar',
    ]
)
