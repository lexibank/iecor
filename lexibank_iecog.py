# coding=utf-8
from __future__ import unicode_literals, print_function

from collections import OrderedDict
from itertools import groupby

from clldutils.dsv import UnicodeWriter, reader
from clldutils.path import Path, remove
from nameparser import HumanName
from pycldf.dataset import Wordlist
from pycldf.sources import Source
from pylexibank.dataset import Dataset as BaseDataset
from sqlalchemy import create_engine

from mappings import FIELD_MAP, AUTHOR_MAP

LANGUAGE_LIST = "Current"
MEANING_LIST = "Jena175"
CONCEPTICON_MAPPING = "raw/Heggarty-2017-200.tsv"


def dicts(name, to_cldf=False):
    res = []
    for item in reader('raw/{0}.csv'.format(name), dicts=True):
        if to_cldf:
            nitem = {}
            for k, v in FIELD_MAP[name].items():
                if v:
                    nitem[v] = item[k].strip()
        else:
            nitem = item
        if name == 'lexeme':
            nitem['Value'] = nitem['Form']
        res.append(nitem)
    return res


def source_to_kw(src):
    res = {'note': src['citation_text']}
    """
description
bookauthor
note
shorthand
editora
authortype
booksubtitle
editoratype
editortype
subtitle
deprecated
TRS
    """
    for k in [
        'author',
        'title',
        'year',
        'booktitle',
        'part',
        'chapter',
        'edition',
        'howpublished',
        'pages',
        'volume',
        'series',
        'number',
        'isbn',
        'institution',
        'editor',
        'publisher',
        ('link', 'url'),
        ('location', 'address'),
        ('journaltitle', 'journal'),
    ]:
        if isinstance(k, tuple):
            k, kk = k
        else:
            kk = k
        if src[k]:
            res[kk] = src[k]
    return res


def iterrefs(type_, refid):
    for id_, items in groupby(
            sorted(dicts(type_), key=lambda i: i[refid]), lambda i: i[refid]):
        refs = [(i['source_id'], i['pages'].replace(';', '|')) for i in items]
        refs = ['{0}{1}'.format(sid, '[{0}]'.format(p) if p else '') for sid, p
                in refs]
        yield id_, refs


class Dataset(BaseDataset):
    id = 'iecog'
    dir = Path(__file__).parent

    @staticmethod
    def db_dump_to_csv():
        def query(db, q):
            res = db.execute(q)
            header = res.keys()
            return header, list(res)

        exclude = [
            'lastEditedBy',
            'lastTouched',
            'modified',
            'logNormalMean',
            'logNormalOffset',
            'logNormalStDev',
            'normalMean',
            'normalStDev',
        ]

        dbc = create_engine('postgresql://postgres@/cobl_old')

        for t in query(dbc, "SELECT tablename FROM pg_catalog.pg_tables")[1]:
            table = t[0]
            if not table.startswith(
                    'lexicon_') or table == 'lexicon_nexusexport':
                continue
            header, rows = query(dbc, 'select * from {0}'.format(table))
            print(table)
            with UnicodeWriter(
                    'raw/{0}.csv'.format(table.partition('_')[2])) as w:
                h = [c for c in header if c not in exclude]
                for c in h:
                    print('    {0}'.format(c))
                w.writerow(h)
                for row in rows:
                    d = OrderedDict(zip(header, row))
                    for k in exclude:
                        if k in d:
                            del d[k]
                    w.writerow(d.values())

    def cmd_download(self, **kw):
        self.db_dump_to_csv()

    def cmd_install(self, **kw):
        authors = {
            '{0} {1}'.format(v['First_Name'], v['Last_Name']): v for v in
            dicts('author', to_cldf=True)}
        author_max_id = max(int(a['ID']) for a in authors.values())

        for p in Path('cldf').iterdir():
            if p.is_file():
                remove(p)

        ds = Wordlist.in_dir('cldf')
        ds['FormTable', 'Form'].required = False
        ds.add_columns('FormTable', 'Value', 'Gloss', 'phon_form', 'Phonemic',
                       'native_script', 'url')
        for src in dicts('source'):
            ds.add_sources(
                Source(src['ENTRYTYPE'], src['id'], **source_to_kw(src)))
        ds.add_component(dict(
            url='authors.csv',
            tableSchema=dict(columns=[
                dict(name='ID'),
                dict(name='Last_Name'),
                dict(name='First_Name'),
                dict(name='URL'),
                dict(name='Photo'),
            ])
        ))

        lrefs = {k: v for k, v in iterrefs('lexemecitation', 'lexeme_id')}
        crefs = {k: v for k, v in
                 iterrefs('cognatejudgementcitation', 'cognate_judgement_id')}
        csrefs = {k: v for k, v in
                  iterrefs('cognateclasscitation', 'cognate_class_id')}

        ds.add_component('ParameterTable', 'Concepticon_ID',
                         'Concepticon_Gloss', 'Concepticon_Definition',
                         'Example_Context')
        ds.add_component('CognateTable')
        ds.add_component(
            'CognatesetTable',
            'Root_Form',
            'Root_Gloss',
            'Root_Language',
            {'name': 'Dyen', 'separator': ";"})
        ds.add_component(
            'LanguageTable',
            {'name': 'Author_ID', 'separator': ';'},
            {'name': 'Earliest_Time_Depth_Bound',
             'datatype': {'base': 'integer', 'minimum': 0}},
            {'name': 'Latest_Time_Depth_Bound',
             'datatype': {'base': 'integer', 'minimum': 0}},
            'Description',
            'Variety',
            'Clade',
            'Color',
            'ascii_name',
            {'name': 'historical', 'datatype': 'boolean'},
            {'name': 'fossil', 'datatype': 'boolean'})
        ds.add_table(
            'loans.csv',
            'Cognateset_ID',
            'SourceCognateset_ID',
            'Comment',
            'Source_languoid',
            'Source_form',
            {'name': 'Parallel_loan_event', 'datatype': 'boolean'},
        )

        clades = {d['id']: d for d in dicts('clade')}
        l2clade = {d['language_id']: clades[d['clade_id']] for d in
                   dicts('languageclade')}

        llists = {d['id']: (d['name'], set()) for d in dicts('languagelist')}
        for llid, _ds in groupby(
                sorted(dicts('languagelistorder'),
                       key=lambda d: d['language_list_id']),
                lambda d: d['language_list_id'],
        ):
            for d in _ds:
                llists[llid][1].add(d['language_id'])
        llists = {v[0]: v[1] for v in llists.values()}

        mlists = {d['id']: (d['name'], set()) for d in dicts('meaninglist')}
        for mlid, _ds in groupby(
                sorted(dicts('meaninglistorder'),
                       key=lambda d: d['meaning_list_id']),
                lambda d: d['meaning_list_id'],
        ):
            for d in _ds:
                mlists[mlid][1].add(d['meaning_id'])
        mlists = {v[0]: v[1] for v in mlists.values()}

        langs = [d for d in dicts('language', to_cldf=True) if
                 d['notInExport'] == 'False' and d['ID'] in llists[
                     LANGUAGE_LIST]]
        lang_urls = {l['ID']: l.pop('url') for l in langs}
        for lang in langs:
            lang.update(
                Clade=l2clade[lang['ID']]['cladeName'],
                Color=l2clade[lang['ID']]['hexColor'])
        lids = set(d['ID'] for d in langs)
        forms = [f for f in dicts('lexeme', to_cldf=True) if
                 f['Form'] and (f['Language_ID'] in lids and f[
                     'Comment'] != 'EXCLUDE.') and f['Parameter_ID'] in mlists[
                     MEANING_LIST]]
        for f in forms:
            if f['url']:
                if f['Language_ID'] in lang_urls:
                    f['url'] = lang_urls[f['Language_ID']] + f['url']
                else:
                    raise ValueError(f['Language_ID'])
            f['Source'] = lrefs.get(f['ID'], [])
        mids = set(f['Parameter_ID'] for f in forms)
        meanings = [d for d in dicts('meaning', to_cldf=True) if
                    d['ID'] in mids]

        cmapping = {d['ID']: d for d in
                    reader(CONCEPTICON_MAPPING, delimiter='\t', dicts=True)}
        for m in meanings:
            m['Concepticon_ID'] = cmapping[m['ID']]['CONCEPTICON_ID']
            m['Concepticon_Gloss'] = cmapping[m['ID']]['CONCEPTICON_GLOSS']
            m['Concepticon_Definition'] = cmapping[m['ID']][
                'CONCEPTICON_DEFINITION']

        for lang in langs:
            lang['historical'] = lang['historical'] == 'True'
            lang['fossil'] = lang['fossil'] == 'True'
            lang['Authors'] = lang['Authors'].split(' and ') if lang[
                'Authors'] else []
            lang['Authors'] = [AUTHOR_MAP.get(a, a) or a for a in
                               lang['Authors']]

            ids = []

            for a in lang['Authors']:
                if a not in authors:
                    author_max_id += 1
                    an = HumanName(a)
                    authors[a] = dict(
                        ID='{0}'.format(author_max_id),
                        Last_Name=an.last,
                        First_Name=an.first,
                        URL=None,
                        photo=None,
                    )
                ids.append(authors[a]['ID'])
            lang['Author_ID'] = ids

        fids = set(f['ID'] for f in forms)
        csids = set()
        cognates = [d for d in dicts('cognatejudgement',
                                     to_cldf=True) if d['Form_ID'] in fids]

        for c in cognates:
            csids.add(c['Cognateset_ID'])
            c['Source'] = crefs.get(c['ID'], [])

        dyen = {
            csid: [d['name'].strip() for d in dyens if d['doubtful'] == 'False']
            for csid, dyens in
            groupby(sorted(dicts('dyencognateset'),
                           key=lambda d: d['cognate_class_id']),
                    lambda d: d['cognate_class_id'])
        }

        css = []
        loans = []

        for cset in dicts('cognateclass', to_cldf=True):
            if cset['ID'] in csids:
                cset['Source'] = csrefs.get(cset['ID'], [])
                cset['Dyen'] = sorted(dyen.get(cset['ID'], []))
                css.append(cset)

                if cset['loanword'] == 'True':
                    loans.append({
                        'Cognateset_ID': cset['ID'],
                        'SourceCognateset_ID': cset['loanSourceCognateClass_id']
                        if cset['loanSourceCognateClass_id'] in csids else None,
                        'Comment': cset['loan_notes'],
                        'Source_languoid': cset['loan_source'],
                        'Source_form': cset['sourceFormInLoanLanguage'],
                        'Parallel_loan_event': cset['parallelLoanEvent'] == 'True',
                    })

        ds.write(
            FormTable=forms,
            LanguageTable=[l for l in langs if l['ID'] in lids],
            ParameterTable=meanings,
            CognateTable=cognates,
            CognatesetTable=css,
            # BorrowingTable=[],
            **{'loans.csv': loans,
               'authors.csv': sorted(authors.values(),
                                     key=lambda d: d['Last_Name'])})
