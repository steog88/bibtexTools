# bibtexTools
author: Stefano Gariazzo <gariazzo@ific.uv.es>

## bibtexImporter.py
This tool is intended to facilitate managing bibliography for LaTeX.
You should use INSPIRES keys for the bibtex entries in order to have a good behaviour of the code.

### Requirements and Configuration
Tested only in Linux and with Python 2.

You may need to install Python package `urllib2` if it is missing.

You must change the configuration variables `bibfolder` and `saveInFile` in the initial part of the script, to match the path of your local database (`bibfolder`) and the name of the file where you want to save the downloaded bibtex entries (`saveInFile`).

### Usage
The script reads the .tex files in a folder and creates a .bib file for the compilation of the .tex document.
Assuming that you want to compile some tex file(s)
`"folder/where/tex/files/are/*.tex"`
and that your .bib file should be called
`"folder/where/tex/files/are/name_of_output.bib"`, use with:

    `python bibtexImporter.py "folder/where/tex/files/are/" "name_of_output.bib"`

Example: `python bibtexImporter.py "/home/username/Documents/projectA/" "bibliography.bib"`

The code reads the .tex files in the given folder to detect which entries must be saved in the given output .bib file,
checks the .bib files in the main local database (_the path **must be** configured in the script_) to copy the entries that are already stored there or fetches the missing ones in INSPIRES.
The downloaded information is saved both in the local database and in the output file.
If the output file already exists, the new content is appended to it.

### Suggestions
* you may use different .bib files in your local database, dividing the entries by subject, for example;
* if you edit the local database, then the personalized information that you need will be used for all your new bibtex files. Entries in the local database will never be overwritten by the script;
* save the new info in a temporal file if you want to manually check the new items before adding them to the local database.

## unicode_to_latex.py
This is a collection of proper conversions into LaTeX characters of some common Unicode characters, like accented letters.
`bibtexImporter.py` uses a simplified version of these characters, where the Unicode are translated to simple ASCII characters and the accents are lost.
