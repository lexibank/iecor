from collections import OrderedDict, defaultdict
from itertools import groupby

from csvw import dsv
from clldutils.path import Path

from nameparser import HumanName
from pycldf.dataset import Wordlist
from pycldf.sources import Source
from pylexibank import Dataset as BaseDataset
from pylexibank import Language, Lexeme, Concept
from sqlalchemy import create_engine
import re
import attr

from mappings import FIELD_MAP, AUTHOR_MAP

LANGUAGE_LIST = "default"
MEANING_LIST = "default"
CONCEPTICON_MAPPING = "raw/Heggarty-2017-200.tsv"


def dicts(name, to_cldf=False):
    res = []
    for item in dsv.reader('raw/{0}.csv'.format(name), dicts=True):
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
        refs = [(i['source_id'],
            "{0}{1}".format(i['pages'].replace(';', '|'),
            "{{{0}}}".format(
                re.sub(r'[\n\r]+', ' ', i['comment'].replace(';', '|'))) if i['comment'] else ''))\
                    for i in items]
        refs = ['{0}{1}'.format(sid, '[{0}]'.format(p.strip()) if p else '') for sid, p
                in refs]
        yield id_, refs

@attr.s
class IECORLanguage(Language):
    Author_ID = attr.ib(default=None)
    Description = attr.ib(default=None)
    Clade = attr.ib(default=None)
    Color = attr.ib(default=None)
    Variety = attr.ib(default=None)
    clade_name = attr.ib(default=None)
    ascii_name = attr.ib(default=None)
    loc_justification = attr.ib(default=None)
    historical = attr.ib(default=False)
    fossil = attr.ib(default=False)
    sort_order = attr.ib(default=None)

@attr.s
class IECORLexeme(Lexeme):
    Gloss = attr.ib(default=None)
    phon_form = attr.ib(default=None)
    Phonemic = attr.ib(default=None)
    native_script = attr.ib(default=None)
    url = attr.ib(default=None)

@attr.s
class IECORConcept(Concept):
    Concepticon_Definition = attr.ib(default=None)
    Description_md = attr.ib(default=None)


class Dataset(BaseDataset):

    id = 'iecor'
    dir = Path(__file__).parent.resolve()

    language_class = IECORLanguage
    lexeme_class = IECORLexeme
    concept_class = IECORConcept

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
            with dsv.UnicodeWriter(
                    'raw/{0}.csv'.format(table.partition('_')[2])) as w:
                h = [c for c in header if c not in exclude]
                for c in h:
                    print('    {0}'.format(c))
                w.writerow(h)
                for row in sorted(rows):
                    d = OrderedDict(zip(header, row))
                    for k in exclude:
                        if k in d:
                            del d[k]
                    w.writerow(d.values())

    def cmd_download(self, args):
        self.db_dump_to_csv()

    def cmd_makecldf(self, args):

        with args.writer as ds:

            used_sources = set()

            def clean_md(t):
                lines = []
                for line in t.splitlines():
                    if line.startswith('#'):
                        line = '##' + line
                    lines.append(line)
                return '\\n'.join(lines)

            shorthand_sources = {} # shorthand to scr_id map

            re_ref = re.compile(r'\{ref\s+([^{]+?)\s*\}', re.IGNORECASE)
            re_cog = re.compile(r'(https?://cobl.info)?/cognate/(\d+)/?', re.IGNORECASE)
            re_lex = re.compile(r'(https?://cobl.info)?/lexeme/(\d+)/?', re.IGNORECASE)
            def parse_links_to_markdown(s):
                # format: [label](type-id)  supported types: src/cog/lex
                # return text for non-found IDs
                if type(s) is list:
                    return [parse_links_to_markdown(i) for i in s]
                ret = s
                ret = re_lex.sub(make_lexeme_link, ret)
                ret = re_cog.sub(make_cognate_link, ret)
                ret = re_ref.sub(make_source_link, ret)
                return ret
            def make_source_link(m):
                shorthand_ref = m.groups()[0]

                # fixes:
                if shorthand_ref == 'Meyer-Lübke 1930–1935':
                    shorthand_ref = 'Meyer-Lübke 1935'

                if shorthand_ref in shorthand_sources:
                    used_sources.add(shorthand_sources[shorthand_ref])
                    return "[%s](src-%s)" % (
                            shorthand_ref,
                            shorthand_sources[shorthand_ref])
                if ':' in shorthand_ref: # : typo {ref Foo 2000:16-18}
                    arr = shorthand_ref.split(':', 2)
                    if arr[0] in shorthand_sources:
                        used_sources.add(shorthand_sources[arr[0]])
                        return "[%s](src-%s):%s" % (
                                arr[0], shorthand_sources[arr[0]], arr[1])
                return shorthand_ref
            def make_cognate_link(m):
                cog_ref = m.groups()[1]
                if cog_ref in csids:
                    return "[cognate set %s](cog-%s)" % (
                            cog_ref,
                            cog_ref)
                return 'cognate set %s' % (cog_ref)
            def make_lexeme_link(m):
                lex_ref = m.groups()[1]
                if lex_ref in fids:
                    return "[lexeme %s](lex-%s)" % (
                            lex_ref,
                            lex_ref)
                return 'lexeme %s' % (lex_ref)

            authors_dict = dicts('author', to_cldf=True)
            initials_author_id = {a['initials']: a['ID'] for a in authors_dict}
            # add programmers
            last_author_id = max(int(a['ID']) for a in authors_dict)
            authors_dict.extend([
                {
                    'ID': str(last_author_id + 1),
                    'Last_Name': 'Bibiko',
                    'First_Name': 'Hans-Jörg',
                    'URL': 'https://www.shh.mpg.de/person/42541/25500'
                },
                {
                    'ID': str(last_author_id + 2),
                    'Last_Name': 'Runge',
                    'First_Name': 'Jakob',
                    'URL': 'https://github.com/runjak'
                }
            ])
            authors = {
                '{0} {1}'.format(v['First_Name'], v['Last_Name']): v for v in
                authors_dict}
            author_max_id = max(int(a['ID']) for a in authors.values())

            # for p in Path('cldf').iterdir():
            #     if p.is_file():
            #         Path.unlink(p)

            for src in dicts('source'):
                shorthand_sources[src['shorthand']] = src['id']

            lrefs = {k: v for k, v in iterrefs('lexemecitation', 'lexeme_id')}
            crefs = {k: v for k, v in
                     iterrefs('cognatejudgementcitation', 'cognate_judgement_id')}
            csrefs = {k: v for k, v in
                      iterrefs('cognateclasscitation', 'cognate_class_id')}

            ds.cldf.add_component(dict(
                url='authors.csv',
                tableSchema=dict(
                    columns=[
                        dict(name='ID'),
                        dict(name='Last_Name'),
                        dict(name='First_Name'),
                        dict(name='URL'),
                        dict(name='Photo'),
                    ],
                    primaryKey=['ID'])
            ))
            ds.cldf.add_component(
                'CognatesetTable',
                'Root_Form',
                'Root_Gloss',
                'Root_Language',
                'Comment',
                'Justification',
                {'name': 'revised_by', 'separator': ";"},
                {'name': 'Ideophonic', 'datatype': 'boolean'},
                {'name': 'Dyen', 'separator': ";"},
                {'name': 'proposedAsCognateTo_pk', 'datatype': {'base': 'integer'}},
                {'name': 'proposedAsCognateToScale', 'datatype': {'base': 'integer'}},
                {'name': 'parallelDerivation', 'datatype': 'boolean'},
                'Root_Form_calc',
                'Root_Language_calc')
            ds.cldf.add_table(
                'loans.csv',
                'Cognateset_ID',
                'SourceCognateset_ID',
                'Comment',
                'Source_languoid',
                'Source_form',
                {'name': 'Parallel_loan_event', 'datatype': 'boolean'},
                primaryKey=['Cognateset_ID'],
            )
            ds.cldf.add_table(
                'policies.csv',
                'id',
                'name',
                'markup_description',
                primaryKey=['id'],
            )
            ds.cldf.add_table(
                'clades.csv',
                'ID',
                'level0_name',
                'level1_name',
                'level2_name',
                'level3_name',
                'clade_name',
                'short_name',
                'color',
                {'name': 'clade_level0','datatype': {'base': 'integer'}},
                {'name': 'clade_level1','datatype': {'base': 'integer'}},
                {'name': 'clade_level2','datatype': {'base': 'integer'}},
                {'name': 'clade_level3','datatype': {'base': 'integer'}},
                {'name': 'at_most','datatype': {'base': 'integer'}},
                {'name': 'at_least','datatype': {'base': 'integer'}},
                'distribution',
                primaryKey=['ID'],
            )

            ds.cldf['LanguageTable', 'Author_ID'].separator = ';'
            ds.cldf['LanguageTable', 'Clade'].separator = ';'
            ds.cldf['LanguageTable', 'historical'].datatype.base = 'boolean'
            ds.cldf['LanguageTable', 'fossil'].datatype.base = 'boolean'
            ds.cldf['LanguageTable', 'sort_order'].datatype.base = 'integer'

            clade_table = sorted(dicts('clade', to_cldf=True),
                                key=lambda x: (
                                    int(x['clade_level0']),
                                    int(x['clade_level1']),
                                    int(x['clade_level2']),
                                    int(x['clade_level3']),
                                    ))
            for i, c in enumerate(clade_table):
                c['color'] = '#%s' % (c['color'])

            clades = {d['id']: d for d in dicts('clade')}
            cladesObj = dicts('clade')
            lcdict = dicts('languageclade')
            l2clade = {d['language_id']: clades[d['clade_id']] for d in lcdict}
            for lc in sorted(lcdict,
                    key=lambda d: d['cladesOrder'], reverse=True):
                llid = lc['language_id']
                if clades[lc['clade_id']]['shortName'] and not 'clade_name' in l2clade[llid]:
                    l2clade[llid]['clade_name'] = clades[lc['clade_id']]['cladeName']
                if not 'cladeNames' in l2clade[llid]:
                    l2clade[llid]['cladeNames'] = []
                l2clade[llid]['cladeNames'].append(clades[lc['clade_id']]['cladeName'])
                l2clade[llid]['cladeNames'] = [x for i, x in enumerate(l2clade[llid]['cladeNames'])
                    if l2clade[llid]['cladeNames'].index(x) == i]

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
            for i, lang in enumerate(sorted(langs, key=lambda x: (
                int(x['level0']), int(x['level1']), int(x['level2']),
                int(x['level3'] or 0), int(x['sortRankInClade'])))):
                lang.update(
                    Clade=l2clade[lang['ID']]['cladeNames'],
                    Color=l2clade[lang['ID']]['hexColor'],
                    clade_name=l2clade[lang['ID']]['clade_name'],
                    sort_order=i+1)
            lids = set(d['ID'] for d in langs)
            forms = [f for f in dicts('lexeme', to_cldf=True) if
                     f['Form'] and (f['Language_ID'] in lids and f[
                         'Comment'] != 'EXCLUDE.') and f['Parameter_ID'] in mlists[
                         MEANING_LIST] and f['not_swadesh_term'] == 'False']
            for f in forms:
                if f['url']:
                    if f['Language_ID'] in lang_urls:
                        f['url'] = lang_urls[f['Language_ID']] + f['url']
                    else:
                        raise ValueError(f['Language_ID'])
                f['Source'] = []
                # f['Source'] = lrefs.get(f['ID'], [])
            mids = set(f['Parameter_ID'] for f in forms)
            meanings = [d for d in dicts('meaning', to_cldf=True) if
                        d['ID'] in mids]

            cmapping = {d['ID']: d for d in
                        dsv.reader(CONCEPTICON_MAPPING, delimiter='\t', dicts=True)}

            wikidir = Path(__file__).resolve().parent.parent / 'CoBL.wiki'
            for m in meanings:
                m['Concepticon_ID'] = cmapping[m['ID']]['CONCEPTICON_ID']
                m['Concepticon_Gloss'] = cmapping[m['ID']]['CONCEPTICON_GLOSS']
                m['Concepticon_Definition'] = cmapping[m['ID']][
                    'CONCEPTICON_DEFINITION']

                wiki_data = ''
                wiki_page = wikidir / 'Meaning:-{0}.md'.format(m['Name'])
                if not wiki_page.exists():
                    print('no wiki page for "%s" found' % (m['Name']))
                    wiki_page = wikidir / 'DO-Meaning:-{0}.md'.format(m['Name'])
                    if wiki_page.exists():
                        wiki_data = '##### Illustrative Context\n_' +\
                            m['exampleContext'] +\
                            '_\n\n> Full meaning definition being reformatted and restructured for publication.'
                else:
                    wiki_data = clean_md(Path.read_text(wiki_page))
                m['Description_md'] = wiki_data

            for lang in langs:
                lang['historical'] = lang['historical'] == 'True'
                lang['fossil'] = lang['fossil'] == 'True'
                lang['Authors'] = re.sub(r'\s*,\s*and\s*',' and ', lang['Authors'])
                lang['Authors'] = re.sub(r'\s*,\s*',' and ', lang['Authors'])
                lang['Authors'] = re.sub(r'\s*&\s*',' and ', lang['Authors'])
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
                c['Doubt'] = False

            dyen = {
                csid: [d['name'].strip() for d in dyens if d['doubtful'] == 'False']
                for csid, dyens in
                groupby(sorted(dicts('dyencognateset'),
                               key=lambda d: d['cognate_class_id']),
                        lambda d: d['cognate_class_id'])
            }

            css = []
            loans = []
            policies = []

            lcdict_sorted = sorted(lcdict, key=lambda x: x['cladesOrder'])
            langs_byRank_sorted = sorted(langs, key=lambda x: x['sortRankInClade'])

            def getCladeFromLanguageIds(languageIds):
                '''
                getCladeFromLanguageIds :: Clade | None
                Tries to find the most specific clade that contains all given languageIds.
                If no such clade can be found returns None.
                '''
                # Calculating clade
                lIdToCladeOrders = defaultdict(dict)  # lId -> cId -> cladesOrder
                for i in lcdict:
                    if i['language_id'] in languageIds:
                        lIdToCladeOrders[i['language_id']][i['clade_id']] = i['cladesOrder']
                # Intersecting clades:
                cladeIdOrderMap = None
                for _, newcIdOrderMap in lIdToCladeOrders.items():
                    if cladeIdOrderMap is None:
                        cladeIdOrderMap = newcIdOrderMap
                    else:
                        intersection = newcIdOrderMap.keys() & cladeIdOrderMap.keys()
                        cladeIdOrderMap.update(newcIdOrderMap)
                        cladeIdOrderMap = {k: v for k, v in cladeIdOrderMap.items()
                                               if k in intersection}
                # Retrieving the Clade:
                if cladeIdOrderMap:
                    cId = min(cladeIdOrderMap, key=cladeIdOrderMap.get)
                    for i in cladesObj:
                        if i['id'] == cId:
                            return i['taxonsetName']
                return None

            def getOrthographics(languageIds, affectedFormIds):
                affectedLangs = list()
                for lid in languageIds:
                    for i in langs_byRank_sorted:
                        if i['ID'] == lid:
                            affectedLangs.append(i['ID'])
                            break
                for lid in affectedLangs:
                    for i in forms:
                        if i['Language_ID'] == lid and i['Form'] != '' and i['ID'] in affectedFormIds:
                            return i['Form']
                return None

            def calculateRootForm(cset):
                # If single lexeme in cognate class, use romanised form
                a = []
                cid = cset['ID']
                for i in cognates:
                    if i['Cognateset_ID'] == cid:
                        a.append(i)
                        if len(a) > 1:
                            break
                if len(a) == 1:
                    a_form_id = a[0]['Form_ID']
                    for i in forms:
                        if i['ID'] == a_form_id:
                            return i['Form']
                # Do we have a loanword?
                if cset['loanword'] == 'True':
                    for i in loans:
                        if i['Cognateset_ID'] == cid:
                            if len(i['Source_form']) > 0:
                                return "(%s)" % i['Source_form']
                            else:
                                break
                # Branch lookup
                affectedFormIds = set(
                    [i['Form_ID'] for i in cognates if i['Cognateset_ID'] == cid]
                )
                affectedLgIds = set(
                        [i['Language_ID'] for i in forms if i['ID'] in affectedFormIds]
                    )
                commonCladeIds = [i['clade_id'] for i in lcdict_sorted if
                                                 i['language_id'] in affectedLgIds]
                if commonCladeIds:
                    commonCladeIds = commonCladeIds[0]
                    affectedLgIdsByClade = [i['language_id'] for i in lcdict_sorted \
                        if i['clade_id'] == commonCladeIds and i['language_id'] in affectedLgIds]
                    foundLangs = list() # order is important
                    for aid in affectedLgIdsByClade:
                        for i in langs_byRank_sorted:
                            if i['ID'] == aid:
                                foundLangs.append(i)
                                break
                    lids = [i['ID'] for i in foundLangs if i['representative'] == 'True']
                    if lids:
                        orthographics = getOrthographics(lids, affectedFormIds)
                        if orthographics:
                            return orthographics
                    lids = [i['ID'] for i in foundLangs if i['exampleLanguage'] == 'True']
                    if lids:
                        orthographics = getOrthographics(lids, affectedFormIds)
                        if orthographics:
                            return orthographics
                    lids = [i['ID'] for i in foundLangs]
                    orthographics = getOrthographics(lids[::-1], affectedFormIds)
                    if orthographics:
                        return orthographics
                return ''

            def calculateRootLanguage(cset):
                # If single lexeme in cognate class, use language name
                a = []
                cid = cset['ID']
                for i in cognates:
                    if i['Cognateset_ID'] == cid:
                        a.append(i)
                        if len(a) > 1:
                            break
                if len(a) == 1:
                    a_form_id = a[0]['Form_ID']
                    for i in forms:
                        if i['ID'] == a_form_id:
                            lgId = i['Language_ID']
                            for j in langs:
                                if j['ID'] == lgId:
                                    return j['Name']
                # Maybe we can find a clade specific to the related languages
                affectedFormIds = [i['Form_ID'] for i in cognates if i['Cognateset_ID'] == cid]
                parentCladeTaxonsetName = getCladeFromLanguageIds(set(
                    i['Language_ID'] for i in forms if i['ID'] in affectedFormIds))
                if parentCladeTaxonsetName is not None:
                    return "(%s)" % parentCladeTaxonsetName
                # Maybe we can use loan_source:
                if cset['loanword'] == 'True':
                    for i in loans:
                        if i['Cognateset_ID'] == cid:
                            if len(i['Source_languoid']) > 0:
                                return "(%s)" % i['Source_languoid']
                            else:
                                break
                return ''

            for cset in dicts('cognateclass', to_cldf=True):
                if cset['ID'] in csids:
                    csrc = csrefs.get(cset['ID'], [])
                    if len(csrc):
                        for s in csrc:
                            sid = re.sub(r'^(\d+).*', r'\1', s)
                            used_sources.add(sid)
                    cset['Source'] = csrefs.get(cset['ID'], [])
                    cset['Dyen'] = sorted(dyen.get(cset['ID'], []))
                    cset['Ideophonic'] = cset['Ideophonic'] == 'True'
                    cset['parallelDerivation'] = cset['parallelDerivation'] == 'True'
                    cset['Comment'] = parse_links_to_markdown(cset['Comment'])
                    cset['Justification'] = parse_links_to_markdown(cset['Justification'])
                    cset['revised_by'] = [initials_author_id[a] for a in cset['revised_by'].split(', ')] if cset['revised_by'] else []
                    if cset['proposedAsCognateTo_pk'] and not cset['proposedAsCognateTo_pk'] in csids:
                        cset['proposedAsCognateTo_pk'] = ''
                        cset['proposedAsCognateToScale'] = 0
                    css.append(cset)

                    if cset['dubiousSet'] == 'True':
                        for c in cognates:
                            if c['Cognateset_ID'] == cset['ID']:
                                c['Doubt'] = True
                                break

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

                    if not cset['Root_Form']:
                        cset['Root_Form_calc'] = calculateRootForm(cset)
                    if not cset['Root_Language']:
                        cset['Root_Language_calc'] = calculateRootLanguage(cset)

            for f in forms:
                f['Comment'] = parse_links_to_markdown(f['Comment'])
                f['Source'] = parse_links_to_markdown(f['Source'])
            for c in css:
                c['Source'] = parse_links_to_markdown(c['Source'])


            for i, p in enumerate([
                        # names of wiki pages come soon
                    ]):
                wiki_page = wikidir / '{0}.md'.format(p)
                if not wiki_page.exists():
                    print('no wiki page for "%s" found' % (p))
                else:
                    policies.append({
                        'id': str(i+1),
                        'name': re.sub(r'^[\d\-]*', '', p).replace('-', ' '),
                        'markup_description': clean_md(Path.read_text(wiki_page)),
                    })

            for src in dicts('source'):
                if src['id'] in used_sources:
                    ds.cldf.add_sources(
                        Source(src['ENTRYTYPE'], src['id'], **source_to_kw(src)))

            renewed_form_id_map = {}

            for m in meanings:
                ds.add_concept(
                    ID = m['ID'],
                    Name = m['Name'],
                    Concepticon_ID = m['Concepticon_ID'],
                    Concepticon_Gloss = m['Concepticon_Gloss'],
                    Concepticon_Definition = m['Concepticon_Definition'],
                    Description_md = m['Description_md'],
                )

            for f in forms:
                nf = ds.add_form(
                    ID=f['ID'],
                    Language_ID=f['Language_ID'],
                    Parameter_ID=f['Parameter_ID'],
                    Value=f['Value'],
                    Form=f['Form'],
                    Comment=f['Comment'],
                    Source=f['Source'],
                    Gloss=f['Gloss'],
                    phon_form=f['phon_form'],
                    Phonemic=f['Phonemic'],
                    native_script=f['native_script'],
                    url=f['url'],
                )
                renewed_form_id_map[f['ID']] = nf['ID']

            for l in langs:
                if l['ID'] in lids:
                    ds.add_language(
                        ID=l['ID'],
                        Name=l['Name'],
                        Glottocode=l['Glottocode'],
                        ISO639P3code=l['ISO639P3code'],
                        Longitude=l['Longitude'],
                        Latitude=l['Latitude'],
                        Author_ID=l['Author_ID'],
                        Description=l['Description'],
                        Variety=l['Variety'],
                        Clade=l['Clade'],
                        clade_name=l['clade_name'],
                        Color=l['Color'],
                        ascii_name=l['ascii_name'],
                        loc_justification=l['loc_justification'],
                        historical=l['historical'],
                        fossil=l['fossil'],
                        sort_order=l['sort_order'],
                    )

            for c in cognates:
                ds.add_cognate(
                    ID = c['ID'],
                    Form_ID = renewed_form_id_map[c['Form_ID']],
                    Cognateset_ID = c['Cognateset_ID'],
                    Doubt = c['Doubt'],
                )

            ds.write(
                CognatesetTable=css,
                **{'loans.csv': loans,
                   'policies.csv': policies,
                   'authors.csv': sorted(authors.values(),
                                         key=lambda d: d['Last_Name']),
                   'clades.csv': clade_table})
