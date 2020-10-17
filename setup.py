from setuptools import setup
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
        'pyconcepticon'
        'pylexibank>=2.7.2',
        'pycdstar',
        'pycldf>=1.15.2',
        'clldutils>=3.5.4',
        'csvw>=1.8',
        'nameparser>=1.0.6',
        'Markdown>=3.2.2',
    ],
    extras_require={
        "test": [
            "pytest-cldf"
        ]
    },
)
