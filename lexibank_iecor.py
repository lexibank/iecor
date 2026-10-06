import re
from itertools import groupby
from collections import OrderedDict, defaultdict
import dataclasses
from typing import Optional

from csvw import dsv
from clldutils.path import Path

from nameparser import HumanName
from pycldf.sources import Source
from pylexibank import Dataset as BaseDataset
from pylexibank import Language, Lexeme, Concept
from sqlalchemy import create_engine
from pyconcepticon import Concepticon

LANGUAGE_LIST = "IE-CoR_1-1"
MEANING_LIST = "JenaFinal170"


def iter_dicts(name, to_cldf=False):
    for item in dsv.reader(f'raw/{name}.csv', dicts=True):
        if to_cldf:
            nitem = {}
            for k, v in FIELD_MAP[name].items():
                if v:
                    nitem[v] = item[k].strip()
        else:
            nitem = item
        if name == 'lexeme':
            nitem['Value'] = nitem['Form']
        yield nitem


def source_to_kw(src):
    res = {'note': src['citation_text']}
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
            sorted(iter_dicts(type_), key=lambda i: i[refid]), lambda i: i[refid]):
        refs = [
            (
                i['source_id'],
                "{0}{1}".format(i['pages'].replace(';', '|'),
                                "{{{0}}}".format(
                                    re.sub(r'[\n\r]+', ' ', i['comment'].replace(';', '|'))) if i['comment'] else '')
            )
            for i in items
        ]
        yield id_, ['{0}{1}'.format(sid, f'[{p.strip()}]' if p else '') for sid, p in refs]


@dataclasses.dataclass
class IECORLanguage(Language):
    """
    An IE-CoR variety.
    """
    Author_ID: Optional[str] = None
    Description: Optional[str] = None
    Clade: Optional[str] = None
    Color: Optional[str] = None
    Variety: Optional[str] = None
    clade_name: Optional[str] = None
    ascii_name: Optional[str] = None
    loc_justification: Optional[str] = None
    historical: Optional[bool] = False
    distribution: Optional[bool] = False
    logNormalMean: Optional[bool] = False
    logNormalOffset: Optional[bool] = False
    logNormalStDev: Optional[bool] = False
    normalMean: Optional[bool] = False
    normalStDev: Optional[bool] = False
    fossil: Optional[bool] = False
    sort_order: Optional[str] = None


@dataclasses.dataclass
class IECORLexeme(Lexeme):
    """
    IE-CoR lexeme.
    """
    Gloss: Optional[str] = None
    phon_form: Optional[str] = None
    Phonemic: Optional[str] = None
    Phonemic_Segments: Optional[str] = None
    native_script: Optional[str] = None
    url: Optional[str] = None


@dataclasses.dataclass
class IECORConcept(Concept):
    """
    IE-CoR concepts often have an additional description.
    """
    Concepticon_Definition: Optional[str] = None
    Description_md: Optional[str] = None


class Dataset(BaseDataset):
    id = 'iecor'
    dir = Path(__file__).parent.resolve()

    language_class = IECORLanguage
    lexeme_class = IECORLexeme
    concept_class = IECORConcept

    def cmd_makecldf(self, args):
        with (args.writer as ds):
            ds.cldf.properties['dc:description'] = \
                ("This dataset is decribed in Anderson et al. 2025 "
                 "[DOI: 10.1038/s41597-025-05445-3](https://doi.org/10.1038/s41597-025-05445-3).")
            used_sources = set()

            def clean_md(t):
                lines = []
                for line in t.splitlines():
                    if line.startswith('#'):
                        line = '##' + line
                    lines.append(line)
                return '\\n'.join(lines)

            shorthand_sources = {}  # shorthand to scr_id map

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
                    return f"[{shorthand_ref}](src-{shorthand_sources[shorthand_ref]})"
                if ':' in shorthand_ref:  # : typo {ref Foo 2000:16-18}
                    arr = shorthand_ref.split(':', 2)
                    if arr[0] in shorthand_sources:
                        used_sources.add(shorthand_sources[arr[0]])
                        return "[{}](src-{}):{}".format(
                            arr[0], shorthand_sources[arr[0]], arr[1])
                return shorthand_ref

            def make_cognate_link(m):
                cog_ref = m.groups()[1]
                if cog_ref in csids:
                    return "[cognate set {}](cog-{})".format(cog_ref, cog_ref)
                return 'cognate set {}'.format(cog_ref)

            def make_lexeme_link(m):
                lex_ref = m.groups()[1]
                if lex_ref in fids:
                    return "[lexeme {}](lex-{})".format(lex_ref, lex_ref)
                return 'lexeme {}'.format(lex_ref)

            authors_dict = list(iter_dicts('author', to_cldf=True))
            initials_author_id = {a['initials']: a['ID'] for a in authors_dict}
            # add programmers
            last_author_id = max(int(a['ID']) for a in authors_dict)
            authors_dict.extend([
                {'ID': str(last_author_id + 1), 'Last_Name': 'Bibiko', 'First_Name': 'Hans-Jörg'},
                {'ID': str(last_author_id + 2), 'Last_Name': 'Runge', 'First_Name': 'Jakob'}
            ])
            authors = {'{0} {1}'.format(v['First_Name'], v['Last_Name']): v for v in authors_dict}
            author_max_id = max(int(a['ID']) for a in authors.values())

            for src in iter_dicts('source'):
                shorthand_sources[src['shorthand']] = src['id']

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
                'Root_Language_calc',
                {'name': 'supersetid', 'datatype': {'base': 'integer'}})
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
                'clades.csv',
                'ID',
                'level0_name',
                'level1_name',
                'level2_name',
                'level3_name',
                'clade_name',
                'short_name',
                'color',
                {'name': 'clade_level0', 'datatype': {'base': 'integer'}},
                {'name': 'clade_level1', 'datatype': {'base': 'integer'}},
                {'name': 'clade_level2', 'datatype': {'base': 'integer'}},
                {'name': 'clade_level3', 'datatype': {'base': 'integer'}},
                'taxonsetName',
                primaryKey=['ID'],
            )

            ds.cldf['FormTable', 'Phonemic_Segments'].separator = " "
            ds.cldf['LanguageTable', 'Author_ID'].separator = ';'
            ds.cldf['LanguageTable', 'Clade'].separator = ';'
            ds.cldf['LanguageTable', 'historical'].datatype.base = 'boolean'
            ds.cldf['LanguageTable', 'fossil'].datatype.base = 'boolean'
            ds.cldf['LanguageTable', 'sort_order'].datatype.base = 'integer'
            ds.cldf['LanguageTable', 'logNormalMean'].datatype.base = 'integer'
            ds.cldf['LanguageTable', 'logNormalOffset'].datatype.base = 'integer'
            ds.cldf['LanguageTable', 'logNormalStDev'].datatype.base = 'float'
            ds.cldf['LanguageTable', 'normalMean'].datatype.base = 'integer'
            ds.cldf['LanguageTable', 'normalStDev'].datatype.base = 'integer'

            clade_cldf = [c for c in iter_dicts('clade', to_cldf=True) if c['export'].strip() == 'True']
            cladesObj = [c for c in iter_dicts('clade') if c['export'].strip() == 'True']

            clade_table = sorted(clade_cldf, key=lambda x: (
                int(x['clade_level0']),
                int(x['clade_level1']),
                int(x['clade_level2']),
                int(x['clade_level3'])))
            for i, c in enumerate(clade_table):
                c['color'] = '#{}'.format(c['color'])
                del c['export']

            clades = {d['id']: d for d in cladesObj}
            lcdict = list(iter_dicts('languageclade'))
            l2clade = {d['language_id']: clades[d['clade_id']] for d in lcdict if d['clade_id'] in clades}
            for lc in sorted(lcdict, key=lambda d: d['cladesOrder'], reverse=True):
                if lc['clade_id'] not in clades:
                    continue
                llid = lc['language_id']
                if clades[lc['clade_id']]['shortName'] and 'clade_name' not in l2clade[llid]:
                    l2clade[llid]['clade_name'] = clades[lc['clade_id']]['cladeName']
                if 'cladeNames' not in l2clade[llid]:
                    l2clade[llid]['cladeNames'] = []
                l2clade[llid]['cladeNames'].append(clades[lc['clade_id']]['cladeName'])
                l2clade[llid]['cladeNames'] = [x for i, x in enumerate(l2clade[llid]['cladeNames'])
                                               if l2clade[llid]['cladeNames'].index(x) == i]

            llists = {d['id']: (d['name'], set()) for d in iter_dicts('languagelist')}
            for llid, _ds in groupby(
                sorted(iter_dicts('languagelistorder'), key=lambda d: d['language_list_id']),
                lambda d: d['language_list_id'],
            ):
                for d in _ds:
                    llists[llid][1].add(d['language_id'])
            llists = {v[0]: v[1] for v in llists.values()}

            mlists = {d['id']: (d['name'], set()) for d in iter_dicts('meaninglist')}
            for mlid, _ds in groupby(
                sorted(iter_dicts('meaninglistorder'), key=lambda d: d['meaning_list_id']),
                lambda d: d['meaning_list_id'],
            ):
                for d in _ds:
                    mlists[mlid][1].add(d['meaning_id'])
            mlists = {v[0]: v[1] for v in mlists.values()}

            langs = [d for d in iter_dicts('language', to_cldf=True) if
                     d['notInExport'] == 'False' and d['ID'] in llists[LANGUAGE_LIST]]
            lang_urls = {lg['ID']: lg.pop('url') for lg in langs}
            for i, lang in enumerate(sorted(langs, key=lambda x: (
                    int(x['level0']), int(x['level1']), int(x['level2']),
                    int(x['level3'] or 0), int(x['sortRankInClade'])))):
                lang.update(
                    Clade=l2clade[lang['ID']]['cladeNames'],
                    Color=l2clade[lang['ID']]['hexColor'],
                    clade_name=l2clade[lang['ID']]['clade_name'],
                    sort_order=i + 1)
            lids = set(d['ID'] for d in langs)
            forms = [f for f in iter_dicts('lexeme', to_cldf=True) if
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
            meanings = [d for d in iter_dicts('meaning', to_cldf=True) if d['ID'] in mids]

            wikidir = Path(__file__).resolve().parent.parent / 'CoBL-public.wiki'
            c_api = Concepticon()
            for m in meanings:
                cl = c_api.conceptsets.get(m['Concepticon_ID'])
                m['Concepticon_Gloss'] = cl.gloss
                m['Concepticon_Definition'] = cl.definition

                wiki_page = wikidir / 'Meaning:-{0}.md'.format(m['Name'])
                assert wiki_page.exists()
                wiki_data = clean_md(Path.read_text(wiki_page))
                m['Description_md'] = wiki_data

            for lang in langs:
                lang['historical'] = lang['historical'] == 'True'
                lang['fossil'] = lang['fossil'] == 'True'
                lang['Authors'] = re.sub(r'\s*,\s*and\s*', ' and ', lang['Authors'])
                lang['Authors'] = re.sub(r'\s*,\s*', ' and ', lang['Authors'])
                lang['Authors'] = re.sub(r'\s*&\s*', ' and ', lang['Authors'])
                lang['Authors'] = lang['Authors'].split(' and ') if lang[
                    'Authors'] else []
                lang['Authors'] = [AUTHOR_MAP.get(a, a) or a for a in lang['Authors']]

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
            cognates = [d for d in iter_dicts('cognatejudgement',
                                              to_cldf=True) if d['Form_ID'] in fids]

            for c in cognates:
                csids.add(c['Cognateset_ID'])
                c['Doubt'] = False

            dyen = {
                csid: [d['name'].strip() for d in dyens if d['doubtful'] == 'False']
                for csid, dyens in
                groupby(sorted(iter_dicts('dyencognateset'),
                               key=lambda d: d['cognate_class_id']),
                        lambda d: d['cognate_class_id'])
            }

            css = []
            loans = []

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
                                return "({})".format(i['Source_form'])
                            else:
                                break
                # Branch lookup
                affectedFormIds = set([i['Form_ID'] for i in cognates if i['Cognateset_ID'] == cid])
                affectedLgIds = set(
                    [i['Language_ID'] for i in forms if i['ID'] in affectedFormIds])
                commonCladeIds = [
                    i['clade_id'] for i in lcdict_sorted if i['language_id'] in affectedLgIds]
                if commonCladeIds:
                    commonCladeIds = commonCladeIds[0]
                    affectedLgIdsByClade = [
                        i['language_id'] for i in lcdict_sorted
                        if i['clade_id'] == commonCladeIds and i['language_id'] in affectedLgIds]
                    foundLangs = list()  # order is important
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
                    return "({})".format(parentCladeTaxonsetName)
                # Maybe we can use loan_source:
                if cset['loanword'] == 'True':
                    for i in loans:
                        if i['Cognateset_ID'] == cid:
                            if len(i['Source_languoid']) > 0:
                                return "({})".format(i['Source_languoid'])
                            else:
                                break
                return ''

            for cset in iter_dicts('cognateclass', to_cldf=True):
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

            for src in iter_dicts('source'):
                if src['id'] in used_sources:
                    ds.cldf.add_sources(
                        Source(src['ENTRYTYPE'], src['id'], **source_to_kw(src)))

            renewed_form_id_map = {}

            for m in meanings:
                ds.add_concept(
                    ID=m['ID'],
                    Name=m['Name'],
                    Concepticon_ID=m['Concepticon_ID'],
                    Concepticon_Gloss=m['Concepticon_Gloss'],
                    Concepticon_Definition=m['Concepticon_Definition'],
                    Description_md=m['Description_md'],
                )

            # remove newly added columns in order to get a good diff
            ds.cldf['FormTable'].tableSchema.columns = [
                c for c in args.writer.cldf['FormTable'].tableSchema.columns
                if c.name != 'Graphemes' and c.name != 'Profile']

            for f in forms:
                # create segements for the fields phon_form and phonemic separately
                # segments of phon_form => Form/Segments
                # segments of phonemic => Form/Phonemic_Segments
                segs = [[''], ['']]
                if f['phon_form'] and f['phon_form'] != ' ':
                    segs[0] = f['phon_form']
                if['Phonemic'] and f['Phonemic'] != ' ':
                    segs[1] = f['Phonemic']
                for i, sf in enumerate(segs):
                    if isinstance(sf, str):
                        # handle space in front of tone marks H/L
                        sf_ = re.sub(r'\s*H', 'H', re.sub(r'\s*L', 'L', sf))
                        # handle cases like foo(x/y)bar => fooxbar
                        sf_ = re.sub(r'\(([^/\)]+?)/[^\)]+?\)', r'\1', sf_)
                        # '/' wrapped by spaces is consistently used as separator
                        sf_ = sf_.replace(' / ', ';')
                        # handle (x) => x; split all variants and take the first one
                        sf_ = re.sub(
                            r'\(([^,;/~L]+?)\)', r'\1', re.split(r' *[,;≠] *', sf_)[0]).strip()
                        sf_ = ds.tokenize({}, sf_) or ['']
                        segs[i] = sf_
                nf = ds.add_form_with_segments(
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
                    Segments=segs[0],
                    Phonemic_Segments=segs[1],
                )
                renewed_form_id_map[f['ID']] = nf['ID']

            for lg in langs:
                lg_dist = ''
                if lg['distribution'] == 'N':
                    lg_dist = 'Normal'
                elif lg['distribution'] == 'O':
                    lg_dist = 'Offset log normal'
                if lg['ID'] in lids:
                    ds.add_language(
                        ID=lg['ID'],
                        Name=lg['Name'],
                        Glottocode=lg['Glottocode'],
                        ISO639P3code=lg['ISO639P3code'],
                        Longitude=lg['Longitude'],
                        Latitude=lg['Latitude'],
                        Author_ID=lg['Author_ID'],
                        Description=lg['Description'],
                        Variety=lg['Variety'],
                        Clade=lg['Clade'],
                        clade_name=lg['clade_name'],
                        Color=lg['Color'],
                        ascii_name=lg['ascii_name'],
                        loc_justification=lg['loc_justification'],
                        historical=lg['historical'],
                        distribution=lg_dist,
                        logNormalMean=int(lg['logNormalMean']) if lg['logNormalMean'] else '',
                        logNormalOffset=int(lg['logNormalOffset']) if lg['logNormalOffset'] else '',
                        logNormalStDev=float(lg['logNormalStDev']) if lg['logNormalStDev'] else '',
                        normalMean=int(lg['normalMean']) if lg['normalMean'] else '',
                        normalStDev=int(lg['normalStDev']) if lg['normalStDev'] else '',
                        fossil=lg['fossil'],
                        sort_order=lg['sort_order'],
                    )

            for c in cognates:
                ds.add_cognate(
                    ID=c['ID'],
                    Form_ID=renewed_form_id_map[c['Form_ID']],
                    Cognateset_ID=c['Cognateset_ID'],
                    Doubt=c['Doubt'],
                )

            ds.write(
                CognatesetTable=css,
                **{'loans.csv': loans,
                   'authors.csv': sorted(authors.values(),
                                         key=lambda d: d['Last_Name']),
                   'clades.csv': clade_table})


AUTHOR_MAP = {
    'Tonya Dewey': 'Tonya Kim Dewey-Findell',
    'Maria Reina Bastardas': 'Maria-Reina Bastardas',
    'Ganesh Gupta': '',
    'Henrik Liljegren': '',
    'Simone Loi': '',
    'Ulrich Geupel': '',
    'Shervin Farridnejad': '',
    'Adam Benkato': '',
    'Mandar Purandare': '',
    'Sam Mersch': '',
    'Borana Lushaj': '',
    'Asfar Ali Khan': '',
    'Patrycja Markus': '',
    'Nicholas Sims-Williams': '',
    'Paul Videsott': '',
    'Paul Versloot': '',
    'Charalambos Christodoulou': '',
    'Guto Rhys': '',
    'Annemarie Verkerk': '',
    'Mojtaba Gheitasi': '',
    'Harald Hammarstr\xf6m': '',
    'Giorgio Cadorini': '',
    'Lo\xefc Cheveau': '',
    'Arash Zeini': '',
    'J\xe9r\xe9mie Delorme': '',
    'Lars Steensland': '',
    'Manuel Widmer': '',
    'Stephen Dworkin': '',
    'Esther Baiwir': '',
    'Khawaja Rehman': '',
    'Sabine Tittel': '',
    'Heather Pagan': '',
}

FIELD_MAP = {
    'author':
        {
            "id": "ID",
            "surname": "Last_Name",
            "firstNames": "First_Name",
            "email": "",
            "website": "URL",
            "initials": "initials",
            "user_id": "",
        },
    'lexeme':  # -> forms.csv
        {
            "id": "ID",
            "language_id": "Language_ID",
            "meaning_id": "Parameter_ID",
            "romanised": "Form",
            "phon_form": "phon_form",
            "gloss": "Gloss",
            "notes": "Comment",
            "_order": "",
            "dubious": "",
            "not_swadesh_term": "not_swadesh_term",
            "phoneMic": "Phonemic",
            "rfcWebLookup1": "url",
            "rfcWebLookup2": "",  # all empty
            "nativeScript": "native_script",
        },
    'language':  # -> languages.csv
        {
            "id": "ID",  # -> id
            "iso_code": "ISO639P3code",  # -> iso639P3code
            "ascii_name": "ascii_name",
            "utf8_name": "Name",  # -> Name
            "description": "Description",
            "earliestTimeDepthBound": "",
            "latestTimeDepthBound": "",
            "progress": "",
            "author": "Authors",
            "foss_stat": "fossil",
            "glottocode": "Glottocode",  # -> glottocode
            "level0": "level0",
            "level1": "level1",
            "level2": "level2",
            "level3": "level3",
            "low_stat": "",  # always False
            "representative": "representative",
            "reviewer": "",
            "rfcWebPath1": "url",
            "rfcWebPath2": "",  # all empty
            "soundcompcode": "",
            "variety": "Variety",
            "sortRankInClade": "sortRankInClade",
            "sndCompLevel0": "",
            "sndCompLevel1": "",
            "sndCompLevel2": "",
            "sndCompLevel3": "",
            "entryTimeframe": "",
            "originalAsciiName": "",
            "historical": "historical",
            "notInExport": "notInExport",
            "distribution": "distribution",
            "logNormalMean": "logNormalMean",
            "logNormalOffset": "logNormalOffset",
            "logNormalStDev": "logNormalStDev",
            "normalMean": "normalMean",
            "normalStDev": "normalStDev",
            "uniformLower": "",
            "uniformUpper": "",
            "latitude": "Latitude",  # -> Latitude
            "longitude": "Longitude",  # -> Longitude
            "exampleLanguage": "exampleLanguage",
            "fragmentary": "",
            "loc_justification": "loc_justification",
        },
    'meaning':  # -> parameters.csv
        {
            "id": "ID",
            "gloss": "Name",
            "description": "",  # always empty!
            "notes": "",  # always empty!
            "percent_coded": "",
            "doubleCheck": "",
            "exclude": "",
            "meaningSetIx": "",
            "tooltip": "Description",
            "meaningSetMember": "",
            "exampleContext": "exampleContext",
            "ixElicitation": "",
            "concepticon_id": "Concepticon_ID",
        },
    'cognatejudgement':  # -> cognates.csv
        {
            "id": "ID",
            "lexeme_id": "Form_ID",
            "cognate_class_id": "Cognateset_ID",
        },
    'cognateclass':
        {
            "id": "ID",
            "root_form": "Root_Form",
            "gloss_in_root_lang": "Root_Gloss",
            "root_language": "Root_Language",
            # alias
            "notes": "Comment",
            "justificationDiscussion": "Justification",
            # name  - always empty

            "loan_notes": "loan_notes",
            "loan_source": "loan_source",  # pretty variable languoid names
            "loanword": "loanword",
            # loanEventTimeDepthBP
            "loanSourceCognateClass_id": "loanSourceCognateClass_id",
            "sourceFormInLoanLanguage": "sourceFormInLoanLanguage",
            # should be put in forms.csv!? (only 509, though)
            "parallelLoanEvent": "parallelLoanEvent",
            # -> if True, split into individual borrowings!

            # notProtoIndoEuropean
            "dubiousSet": "dubiousSet",
            "parallelDerivation": "parallelDerivation",
            "revisedBy": "revised_by",
            # revisedYet
            "ideophonic": "Ideophonic",
            "proposedAsCognateTo_id": "proposedAsCognateTo_pk",
            "proposedAsCognateToScale": "proposedAsCognateToScale",
            "supersetid": "supersetid",
        },
    'clade': # -> clades.csv
        {
            "id": "ID",
            "cladeName": "clade_name",
            "hexColor": "color",
            "shortName": "short_name",
            "taxonsetName": "taxonsetName",
            "export": "export",
            "atMost": "",
            "atLeast": "",
            "cladeLevel0": "clade_level0",
            "cladeLevel1": "clade_level1",
            "cladeLevel2": "clade_level2",
            "cladeLevel3": "clade_level3",
            "level0Name": "level0_name",
            "level1Name": "level1_name",
            "level2Name": "level2_name",
            "level3Name": "level3_name"
        }
}
