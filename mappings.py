AUTHOR_MAP = {
    'Tonya Dewey': 'Tonya Kim Dewey-Findell',
    'Maria-Reina Bastardas': 'Maria Reina Bastardas',
    'Tijmen Pronk': 'Tijman Pronk',
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

"""
clade
    id
    cladeName
    hexColor
    shortName
    export
    exportDate
    taxonsetName
    atMost
    atLeast
    distribution
    uniformUpper  # always empty
    uniformLower  # always empty
    cladeLevel0
    cladeLevel1
    cladeLevel2
    cladeLevel3
    level0Name
    level1Name
    level2Name
    level3Name
languagelist
    id
    name
    description
languageclade
    id
    cladesOrder
    clade_id
    language_id
romanisedsymbol
    id
    symbol
sndcomp
    id
    lgSetName
    lv0
    lv1
    lv2
    lv3
    cladeLevel0
    cladeLevel1
    cladeLevel2
    cladeLevel3
meaninglist
    id
    name
    description
languagelistorder
    id
    language_id
    language_list_id
    order
"""

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
            "distribution": "",
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
            # dubiousSet:                 always True
            # parallelDerivation:         13 True
            "revisedBy": "revised_by",
            # revisedYet
            "ideophonic": "Ideophonic",
            "proposedAsCognateTo_id": "proposedAsCognateTo_pk",
            "proposedAsCognateToScale": "proposedAsCognateToScale",
        },
    'clade': # -> clades.csv
        {
            "id": "ID",
            "cladeName": "clade_name",
            "hexColor": "color",
            "shortName": "short_name",
            "taxonsetName": "",
            "atMost": "at_most",
            "atLeast": "at_least",
            "distribution": "distribution",
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

"""
meaninglistorder
    id
    meaning_id
    meaning_list_id
    order
*citation
    reliability     A|B|C|X
"""
