<a name="ds-cldfmetadatajson"> </a>

# Wordlist CLDF dataset derived from Heggarty, Paul & Anderson, Cormac & Scarborough, Matthew’s "Indo-European Cognate Relationships database" ([IE-CoR version 1.0](https://github.com/lexibank/iecor/releases/tag/v1.0)) from 2019

**CLDF Metadata**: [cldf-metadata.json](./cldf-metadata.json)

**Sources**: [sources.bib](./sources.bib)

property | value
 --- | ---
[dc:bibliographicCitation](http://purl.org/dc/terms/bibliographicCitation) | Heggarty, Paul & Anderson, Cormac & Scarborough, Matthew 2024. Indo-European Cognate Relationships database (IE-CoR version 1.1). Leipzig: Max Planck Institute for Evolutionary Anthropology
[dc:conformsTo](http://purl.org/dc/terms/conformsTo) | [CLDF Wordlist](http://cldf.clld.org/v1.0/terms.rdf#Wordlist)
[dc:identifier](http://purl.org/dc/terms/identifier) | https://iecor.clld.org
[dc:license](http://purl.org/dc/terms/license) | https://creativecommons.org/licenses/by/4.0/
[dcat:accessURL](http://www.w3.org/ns/dcat#accessURL) | https://github.com/lexibank/iecor
[prov:wasDerivedFrom](http://www.w3.org/ns/prov#wasDerivedFrom) | <ol><li><a href="https://github.com/lexibank/iecor/tree/v1.1">lexibank/iecor v1.1</a></li><li><a href="https://github.com/glottolog/glottolog/tree/v5.0">Glottolog v5.0</a></li><li><a href="https://github.com/concepticon/concepticon-data/tree/v3.2.0">Concepticon v3.2.0</a></li><li><a href="https://github.com/cldf-clts/clts/tree/v2.3.0">CLTS v2.3.0</a></li></ol>
[prov:wasGeneratedBy](http://www.w3.org/ns/prov#wasGeneratedBy) | <ol><li><strong>lingpy-rcParams</strong>: <a href="./lingpy-rcParams.json">lingpy-rcParams.json</a></li><li><strong>python</strong>: 3.12.4</li><li><strong>python-packages</strong>: <a href="./requirements.txt">requirements.txt</a></li></ol>
[rdf:ID](http://www.w3.org/1999/02/22-rdf-syntax-ns#ID) | iecor
[rdf:type](http://www.w3.org/1999/02/22-rdf-syntax-ns#type) | http://www.w3.org/ns/dcat#Distribution


## <a name="table-formscsv"></a>Table [forms.csv](./forms.csv)

property | value
 --- | ---
[dc:conformsTo](http://purl.org/dc/terms/conformsTo) | [CLDF FormTable](http://cldf.clld.org/v1.0/terms.rdf#FormTable)
[dc:extent](http://purl.org/dc/terms/extent) | 25731


### Columns

Name/Property | Datatype | Description
 --- | --- | --- 
[ID](http://cldf.clld.org/v1.0/terms.rdf#id) | `string` | Primary key
[Local_ID](http://purl.org/dc/terms/identifier) | `string` | 
[Language_ID](http://cldf.clld.org/v1.0/terms.rdf#languageReference) | `string` | References [languages.csv::ID](#table-languagescsv)
[Parameter_ID](http://cldf.clld.org/v1.0/terms.rdf#parameterReference) | `string` | References [parameters.csv::ID](#table-parameterscsv)
[Value](http://cldf.clld.org/v1.0/terms.rdf#value) | `string` | 
[Form](http://cldf.clld.org/v1.0/terms.rdf#form) | `string` | 
[Segments](http://cldf.clld.org/v1.0/terms.rdf#segments) | list of `string` (separated by ` `) | 
[Comment](http://cldf.clld.org/v1.0/terms.rdf#comment) | `string` | 
[Source](http://cldf.clld.org/v1.0/terms.rdf#source) | list of `string` (separated by `;`) | References [sources.bib::BibTeX-key](./sources.bib)
`Cognacy` | `string` | 
`Loan` | `boolean` | 
`Gloss` | `string` | 
`phon_form` | `string` | 
`Phonemic` | `string` | 
`Phonemic_Segments` | list of `string` (separated by ` `) | 
`native_script` | `string` | 
`url` | `string` | 

## <a name="table-languagescsv"></a>Table [languages.csv](./languages.csv)

property | value
 --- | ---
[dc:conformsTo](http://purl.org/dc/terms/conformsTo) | [CLDF LanguageTable](http://cldf.clld.org/v1.0/terms.rdf#LanguageTable)
[dc:extent](http://purl.org/dc/terms/extent) | 160


### Columns

Name/Property | Datatype | Description
 --- | --- | --- 
[ID](http://cldf.clld.org/v1.0/terms.rdf#id) | `string` | Primary key
[Name](http://cldf.clld.org/v1.0/terms.rdf#name) | `string` | 
[Glottocode](http://cldf.clld.org/v1.0/terms.rdf#glottocode) | `string` | 
`Glottolog_Name` | `string` | 
[ISO639P3code](http://cldf.clld.org/v1.0/terms.rdf#iso639P3code) | `string` | 
[Macroarea](http://cldf.clld.org/v1.0/terms.rdf#macroarea) | `string` | 
[Latitude](http://cldf.clld.org/v1.0/terms.rdf#latitude) | `decimal`<br>&ge; -90<br>&le; 90 | 
[Longitude](http://cldf.clld.org/v1.0/terms.rdf#longitude) | `decimal`<br>&ge; -180<br>&le; 180 | 
`Family` | `string` | 
`Author_ID` | list of `string` (separated by `;`) | 
`Description` | `string` | 
`Clade` | list of `string` (separated by `;`) | 
`Color` | `string` | 
`Variety` | `string` | 
`clade_name` | `string` | 
`ascii_name` | `string` | 
`loc_justification` | `string` | 
`historical` | `boolean` | 
`distribution` | `string` | 
`logNormalMean` | `integer` | 
`logNormalOffset` | `integer` | 
`logNormalStDev` | `float` | 
`normalMean` | `integer` | 
`normalStDev` | `integer` | 
`fossil` | `boolean` | 
`sort_order` | `integer` | 

## <a name="table-parameterscsv"></a>Table [parameters.csv](./parameters.csv)

property | value
 --- | ---
[dc:conformsTo](http://purl.org/dc/terms/conformsTo) | [CLDF ParameterTable](http://cldf.clld.org/v1.0/terms.rdf#ParameterTable)
[dc:extent](http://purl.org/dc/terms/extent) | 170


### Columns

Name/Property | Datatype | Description
 --- | --- | --- 
[ID](http://cldf.clld.org/v1.0/terms.rdf#id) | `string` | Primary key
[Name](http://cldf.clld.org/v1.0/terms.rdf#name) | `string` | 
[Concepticon_ID](http://cldf.clld.org/v1.0/terms.rdf#concepticonReference) | `string` | 
`Concepticon_Gloss` | `string` | 
`Concepticon_Definition` | `string` | 
`Description_md` | `string` | 

## <a name="table-cognatescsv"></a>Table [cognates.csv](./cognates.csv)

property | value
 --- | ---
[dc:conformsTo](http://purl.org/dc/terms/conformsTo) | [CLDF CognateTable](http://cldf.clld.org/v1.0/terms.rdf#CognateTable)
[dc:extent](http://purl.org/dc/terms/extent) | 25741


### Columns

Name/Property | Datatype | Description
 --- | --- | --- 
[ID](http://cldf.clld.org/v1.0/terms.rdf#id) | `string` | Primary key
[Form_ID](http://cldf.clld.org/v1.0/terms.rdf#formReference) | `string` | References [forms.csv::ID](#table-formscsv)
[Form](http://linguistics-ontology.org/gold/2010/FormUnit) | `string` | 
[Cognateset_ID](http://cldf.clld.org/v1.0/terms.rdf#cognatesetReference) | `string` | References [cognatesets.csv::ID](#table-cognatesetscsv)
`Doubt` | `boolean` | 
`Cognate_Detection_Method` | `string` | 
[Source](http://cldf.clld.org/v1.0/terms.rdf#source) | list of `string` (separated by `;`) | References [sources.bib::BibTeX-key](./sources.bib)
[Alignment](http://cldf.clld.org/v1.0/terms.rdf#alignment) | list of `string` (separated by ` `) | 
`Alignment_Method` | `string` | 
`Alignment_Source` | `string` | 

## <a name="table-authorscsv"></a>Table [authors.csv](./authors.csv)

property | value
 --- | ---
[dc:extent](http://purl.org/dc/terms/extent) | 91


### Columns

Name/Property | Datatype | Description
 --- | --- | --- 
`ID` | `string` | Primary key
`Last_Name` | `string` | 
`First_Name` | `string` | 
`URL` | `string` | 
`Photo` | `string` | 

## <a name="table-cognatesetscsv"></a>Table [cognatesets.csv](./cognatesets.csv)

property | value
 --- | ---
[dc:conformsTo](http://purl.org/dc/terms/conformsTo) | [CLDF CognatesetTable](http://cldf.clld.org/v1.0/terms.rdf#CognatesetTable)
[dc:extent](http://purl.org/dc/terms/extent) | 4981


### Columns

Name/Property | Datatype | Description
 --- | --- | --- 
[ID](http://cldf.clld.org/v1.0/terms.rdf#id) | `string`<br>Regex: `[a-zA-Z0-9_\-]+` | Primary key
[Description](http://cldf.clld.org/v1.0/terms.rdf#description) | `string` | 
[Source](http://cldf.clld.org/v1.0/terms.rdf#source) | list of `string` (separated by `;`) | References [sources.bib::BibTeX-key](./sources.bib)
`Root_Form` | `string` | 
`Root_Gloss` | `string` | 
`Root_Language` | `string` | 
`Comment` | `string` | 
`Justification` | `string` | 
`revised_by` | list of `string` (separated by `;`) | 
`Ideophonic` | `boolean` | 
`Dyen` | list of `string` (separated by `;`) | 
`proposedAsCognateTo_pk` | `integer` | 
`proposedAsCognateToScale` | `integer` | 
`parallelDerivation` | `boolean` | 
`Root_Form_calc` | `string` | 
`Root_Language_calc` | `string` | 
`supersetid` | `integer` | 

## <a name="table-loanscsv"></a>Table [loans.csv](./loans.csv)

property | value
 --- | ---
[dc:extent](http://purl.org/dc/terms/extent) | 1036


### Columns

Name/Property | Datatype | Description
 --- | --- | --- 
`Cognateset_ID` | `string` | Primary key
`SourceCognateset_ID` | `string` | 
`Comment` | `string` | 
`Source_languoid` | `string` | 
`Source_form` | `string` | 
`Parallel_loan_event` | `boolean` | 

## <a name="table-cladescsv"></a>Table [clades.csv](./clades.csv)

property | value
 --- | ---
[dc:extent](http://purl.org/dc/terms/extent) | 27


### Columns

Name/Property | Datatype | Description
 --- | --- | --- 
`ID` | `string` | Primary key
`level0_name` | `string` | 
`level1_name` | `string` | 
`level2_name` | `string` | 
`level3_name` | `string` | 
`clade_name` | `string` | 
`short_name` | `string` | 
`color` | `string` | 
`clade_level0` | `integer` | 
`clade_level1` | `integer` | 
`clade_level2` | `integer` | 
`clade_level3` | `integer` | 
`taxonsetName` | `string` | 

