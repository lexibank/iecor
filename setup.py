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
        ],
        'cldfbench.commands': [
            'iecor=iecorcommands',
        ],
    },
    install_requires=[
        'pyconcepticon>=2.8.0'
        'pylexibank>=3.3.0',
        'pycdstar>=1.0.1',
        'pycldf>=1.23.0',
        'clldutils>=3.9.0',
        'csvw>=1.11.0',
        'nameparser>=1.0.6',
        'Markdown>=3.3.4',
    ],
    extras_require={
        "test": [
            "pytest-cldf"
        ]
    },
)
