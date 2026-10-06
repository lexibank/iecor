## Orthography, Transliteration and Transcriptions

In IE-CoR, each lexeme in each language should be represented on up to four levels :
- In the normal, original **orthography** for that language, e.g. Cyrillic or Devanāgarī.
- If that orthography is not a Roman script, then also in an established **transliteration**.  
- In IPA **phoneMic transcription**, following an established phonological analysis of that language.
- In IPA **phoneTic transcription**, to the level of distinguishing major allophones.

As an example of the four levels for a single language, see:
https://iecor.clld.org/languages/greekancient


### Which Script and Symbols?  Local Conventions vs. Universal Standards

In orthography, transliteration and transcription, IE-CoR faces some contrasting imperatives.  We need to respect already long-established conventions specific to a given language and how it is represented.  But we also need to make the database public, so that it can be interpreted and analysed by all, in consistent ways.  

The best balance between local conventions and universal standards is different, then, on each of our four representation levels:
* In the **orthography**, it is fine and expected that you will stick closely to language-specific (or region-specific) conventions in spelling.  
* In the **transliteration** into Roman script, again some language-specific or local usage will often be necessary, although when in doubt, please tend to usage that is more modern and more compatible with other languages.
* Since the **phoneMic** level is still abstract, although it may be possible to tolerate some language-specific conventions, that is to be avoided wherever possible. Please aim for as much standardisation as possible around the precise IPA symbol for the major, default or ‘elsewhere’ allophone of that phoneme.
* On the **phoneTic** transcriptions should use only, and strictly, the symbols of the IPA, in Unicode, not any idiosyncratic language-or region-specific conventions. 


### Which Citation Form?

* Please use the citation form most consistent with that used in most other languages.  So in Latin, for example, verbs are given not in the first person singular, even though that is traditional in Latin dictionaries, but in the infinitive, for consistency with most other languages.
* Please do not add extra free (unbound) morphemes that are extraneous to the root, just because they are often used in citation forms.  For example, in English verbs are _not_ to be cited with preceding 'to', i.e. 'see', not 'to see'.  IE-CoR is fundamentally about root cognacy, and about lexicon, not the grammar of whether the infinitive form in most contexts requires a supporting other free morpheme like 'to'. Note that no normal dictionary of English cites all verbs under 'to …'. IE-CoR should not do so either.


### Lower Case -- and Beware Upper Case Entries

All orthographic entries should be given in lower case. If there are already some entries for your language given in upper case, then they must be corrected to lower case. The only cases where words should be allowed with an initial upper case letter are those where the standard orthography for that language requires it, i.e. on nouns in German.  So German _Haus_ but English _house_.

Entries in upper case should also ring alarm bells: these are very old, legacy and often very unreliable entries. Pease pay special attention to these entries, to consider whether they are really the appropriate lexemes. You should have no hesitation in excluding or correcting them as necessary.  Do not consider that as existing entries they need to be kept!


### Orthography

IE-CoR aims to represent and be in line with the leading scholarship on each of the languages covered.  Often, specialists in particular languages have their own conventions for spelling, transliterating and transcribing individual languages. These differ from script to script, and language to language.  Ancient languages, of course, often had their own dedicated but also idiosyncratic scripts.  

The main, orthographic entry for a lexeme is thus always to be given in whichever is the most established and widely used standard for that language.

Where there are competing alternatives, the general preference is for the more modern one, and the one more compatible with orthographies for other languages, especially if closely related.


### Transliteration  \(into Roman script)

IE-CoR is a very broad comparative database, spanning languages that use a multitude of scripts, including ancient inscriptions.  Very few viewers of the website are likely to be highly familiar with all of them.  So for any language whose orthography is given in a non-Roman script, we also need a **transliteration into Roman script**. 
 
There can be competing approaches for a single language, e.g. for transliterating Russian into Roman script.  In such cases, the expert for that language should choose the most widely used and respected.  This will often be the most recent alternative, and an ISO system.  If in doubt, contact the IE-CoR administrators.


### PhoneMic Transcription 

The IE-CoR database will also be used for qualitative and quantitative searches and analyses in both phonetics and phonology, e.g. to find all tokens in all languages of a particularly sound, or sound sequence.  That is why we also ultimately need both phonemic and (major allophone) phonetic transcriptions of all lexeme entries.  It is also why transcriptions on both levels need to be as consistent and standardised as possible. 

If absolutely necessary, and since the phoneMic level is still abstract, some language-specific conventions may sometimes be tolerated here -- but please check first with the IE-CoR administrators.  Nonetheless, the preference is definitely for as much standardisation as possible around the precise IPA symbol for the major, default or ‘elsewhere’ allophone of that phoneme – not just the simplest symbol to type on a keyboard!  

This is because users cannot be expected to familiar with language-specific conventions in every language.  
So for example, in Standard British English, the phoneme often represented /r/ is of course not a trill, and should ideally be ɾ represented /ɹ/ instead, since [ɹ] is its default allophone. 

On IE-CoR’s precise and strict usage of IPA, see the next section below. 


### PhoneTic Transcription

Obviously, **phoneTic transcriptions** need to be in symbols of the [International Phonetic Alphabet](https://en.wikipedia.org/wiki/International_Phonetic_Alphabet), and **IPA only, nothing else**.  

Please do not use other regional approaches such as the traditional ‘Americanist’ transcriptions, even if they are common for researchers in your language.  So for example, please:
* Use \[y] \(not ü) for the rounded front high vowel.
* Use \[ʃ] \(not š) for the voiceless palato-alveolar fricative.
* Use the dedicated raised characters such as labialised \[ʷ] and palatalised \[ʲ], not superscript of a normal w and j \(not possible anyway in our web entry form).

For more examples, see under the conventions for Indo-European in the next section below.

Please also take care to use the correct, precise IPA symbols where there are multiple similar ones, e.g. 
* Use \[β] \(not 'Eszett' ß) for a voiced bilabial fricative, and its lowered equivalent for the corresponding approximant 
* For accent marks and diacritics, use the correct combining characters, not the standalone characters with space.
* Some diacritics have multiple variants in Unicode, for thinner target characters like \[i], or wider ones like \[m]).
* Please mark vowel length, with the correct IPA symbols \[ː] \(not colon :), \[ˑ], \[  ̆ ]
* Please do mark primary stressed syllables, with the correct IPA symbol \[ˈ].
* Please be accurate with exact Unicode symbols like apostrophes, rough breathings, etc..
* Please distinguish correctly between palatal stops \(e.g. \[ɲ]) and \(secondary articulation) palatalised stops \(e.g. [nʲ]).

There are of course occasional cases where many linguists do not follow IPA usage, e.g. in marking tone.  If you are minded to use any notation different to IPA, however, please check with the IE-CoR administrators first.

Wikipedia has many good, detailed pages on IPA phonetic symbols and their corresponding Unicode character(s).  Just type en.wikipedia.org/wiki/ followed by the symbol character:  <e.g. en.wikipedia.org/wiki/ʃ>.  

You can also search for characters on the Wikipedia page on the [IPA](https://en.wikipedia.org/wiki/International_Phonetic_Alphabet), and just copy individual symbols from there.  That should give you the Unicode symbol to paste directly into the IE-CoR website.  

Another useful 'trick' is to paste a single symbol into a Microsoft Word document, select it, then do Insert —- Symbol. That will give you a description and the Unicode reference number for that character. 

If you need further advice on setting up dedicated keyboard shortcuts for special characters, ask the IE-CoR administrators.


### Transcription Policy: Proto-Indo-European

For the transcription of Proto-Indo-European reconstructed forms, IE-CoR generally follows the system used in LIV², with the major exception that superscripts used for labiovelars are based on the symbol w rather than u̯.  That is, they use the (i.e. ‘hard-coded superscript’) character ʷ, as in *gʷem- '(wohin)gehen, kommen' or *gʷʰen- 'schlagen'.  Do not use any superscript version of u̯.  

Note that as with all such ‘superscript’ or ‘subscript’ characters, these have to be entered with the dedicated unicode characters into which superscript is ‘hard-coded’.  No superscript ‘formatting’ should or even can be used in CoBL/IE-CoR:  see below for the exact unicode characters in each case.  You should be able to copy them from here, if necessary, and paste into the CoBL website online.

These are the following general conventions:

- For palatovelars use the dedicated unicode character combining inverted breve ̑  (U+0311), i.e. *k̑, *g̑, *g̑ʰ.
- For labiovelars use the dedicated unicode character superscript ʷ (U+02B7), i.e. *kʷ, *gʷ, *gʷʰ
- For (voiced-)aspirated consonants use the dedicated unicode character superscript ʰ (U+02B0), i.e. *bʰ, *dʰ, *g̑ʰ, *gʰ, *gʷʰ
- For laryngeals use the dedicated unicode characters ₁ (U+2081) ₂ (U+2082) ₃ (U+2083) for subscript numbers, i.e. *h₁, *h₂, *h₃.  When the precise identity of the reconstructed laryngeal is unknown, use capital H.  If the candidate unknown laryngeal can be narrowed down to two of the three, still use *H, and the specific information may be related in the etymological notes field in the database.

In general, PIE Reconstructions are do be done phonologically as far as it is possible to do so.  Effectively this means to avoid introducing reconstructed */a/ and */o/ unless you are fairly confident that this was the actual identity of a morphophonologically ablauting vowel. Avoid introducing allophonic 'vowel-colouring' effects from laryngeals into the reconstructions, for example:

- *h₂ég̑-e-ti ‘(s)he drives’ (present) not *h₂ág̑-e-ti
- *h₁e-déh₃-t ‘(s)he gave’ (aorist) not *h₁e-dóh₃-t
- *h₁le-h₁lóu̯dʰ-h₂e ‘I am gone’ (perfect) not *h₁le-h₁lóu̯dʰ-h₂a

An important exception to this rule pertains to the liquids, nasals, and glides: In many cases the syllabicity of the liquids, nasals, and glides were morphophonologically determined.  Because syllabification is relevant phonological information, please notate them using the respective combining diacritics:

- For syllabic liquids and nasals used the dedicated unicode combining ring below ̥  (U+0325), i.e *r̥, *l̥, *m̥, *n̥.
- For notation of non-syllabic glides use the dedicated unicode combining breve below ̯  (U+032F), i.e. *i̯, *u̯.

E.g. *k̑léu̯os ń̥dʰgʷʰtom 'imperishable fame' (> Ved. śrávo ’kṣitam, Gk. κλέος ἄφθιτον), not *k̑léuos ńdʰgʷʰitom.

Finally, insofar it is possible to ascertain the position of the PIE accent, include this information by using a combining acute accent over the accented syllable peak.  If the position of the accent is unknown, this information may be omitted.
