# PDF Number Parser

This package can be used to read PDF files and select sentences that
include any numbers in them. The original purpose of this package was to
scan PDF files of overly verbose NGO reports and find the hard numbers 
that are indicative of the NGO's progress in reaching its goals.

What this program does particularly well is locating numbers written
in English and translating them to float data types, e.g. "five hundred
and twenty one" ==> 521.0.

Import:<br/>
`import pdf_number_search.number_sentence_parser as nsp`

Create instance:<br/>
`runner = nsp.PDFNumberFinder(pdf_file=<path_to_pdf>)`

Run:<br/>
`runner.run_number_sentence_translator()`
