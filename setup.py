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
        'pyconcepticon>=3.0.0',
        'pylexibank>=3.4.0',
        'pycdstar>=1.1.0',
        'pycldf>=1.34.0',
        'clldutils>=3.14.0',
        'csvw>=3.1.3',
        'nameparser>=1.1.2',
        'Markdown>=3.4.1',
        'python-nexus>=2.8.0',
    ],
    extras_require={
        "test": [
            "pytest-cldf"
        ]
    },
)
