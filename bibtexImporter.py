#!/usr/bin/env python

"""
author: Stefano Gariazzo <gariazzo@ific.uv.es>

Read the .tex files in a folder and creates a .bib file for the compilation of the .tex document.
You should use INSPIRES keys for the bibtex entries in order to have a good behaviour of the code.

Usage:
python bibtexImporter.py "folder/where/tex/files/are/" "name_of_output.bib"
assuming that you want to compile some tex file(s):
"folder/where/tex/files/are/*.tex"
and that your .bib file should be called:
"folder/where/tex/files/are/name_of_output.bib".

The code reads the texs to detect which entries must be saved in the output .bib file,
checks the .bib files in the main local database (path configured in the script) to copy the entries that are already stored there
or fetches the missing ones in INSPIRES. The downloaded information is saved both in the local database and in the output file.
"""

import sys,re,os
try:
    # For Python 3.0 and later
    from urllib.request import urlopen
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen

from bibtexToolsConfig import bibfolder, saveInFile

################################################################
# unicode characters replacements.
# INSPIRES has the bad habit of using non-ascii characters that can't be saved properly in non-unicode files.
# just convert the bad characters into standard ones.
unicode_to_latex = {
    u"\u00C0": "A",
    u"\u00C1": "A",
    u"\u00C2": "A",
    u"\u00C3": "A",
    u"\u00C4": "A",
    u"\u00C5": "AA",
    u"\u00C6": "AE",
    u"\u00C7": "C",
    u"\u00C8": "E",
    u"\u00C9": "E",
    u"\u00CA": "E",
    u"\u00CB": "E",
    u"\u00CC": "I",
    u"\u00CD": "I",
    u"\u00CE": "I",
    u"\u00CF": "I",
    u"\u00D0": "DH",
    u"\u00D1": "N",
    u"\u00D2": "O",
    u"\u00D3": "O",
    u"\u00D4": "O",
    u"\u00D5": "O",
    u"\u00D6": "O",
    u"\u00D8": "O",
    u"\u00D9": "U",
    u"\u00DA": "U",
    u"\u00DB": "U",
    u"\u00DC": "U",
    u"\u00DD": "Y",
    u"\u00DE": "TH",
    u"\u00DF": "ss",
    u"\u00E0": "a",
    u"\u00E1": "a",
    u"\u00E2": "a",
    u"\u00E3": "a",
    u"\u00E4": "a",
    u"\u00E5": "aa",
    u"\u00E6": "ae",
    u"\u00E7": "c",
    u"\u00E8": "e",
    u"\u00E9": "e",
    u"\u00EA": "e",
    u"\u00EB": "e",
    u"\u00EC": "i",
    u"\u00ED": "i",
    u"\u00EE": "i",
    u"\u00EF": "i",
    u"\u00F0": "dh",
    u"\u00F1": "n",
    u"\u00F2": "o",
    u"\u00F3": "o",
    u"\u00F4": "o",
    u"\u00F5": "o",
    u"\u00F6": "o",
    u"\u00F8": "o",
    u"\u00F9": "u",
    u"\u00FA": "u",
    u"\u00FB": "u",
    u"\u00FC": "u",
    u"\u00FD": "y",
    u"\u00FE": "th",
    u"\u00FF": "y",
    u"\u0100": "A",
    u"\u0101": "a",
    u"\u0102": "A",
    u"\u0103": "a",
    u"\u0104": "A",
    u"\u0105": "a",
    u"\u0410": "A",
    u"\u0106": "C",
    u"\u0107": "c",
    u"\u0108": "C",
    u"\u0109": "c",
    u"\u010A": "C",
    u"\u010B": "c",
    u"\u010C": "C",
    u"\u010D": "c",
    u"\u010E": "D",
    u"\u010F": "d",
    u"\u0110": "DJ",
    u"\u0111": "dj",
    u"\u0112": "E",
    u"\u0113": "e",
    u"\u0114": "E",
    u"\u0115": "e",
    u"\u0116": "E",
    u"\u0117": "e",
    u"\u0118": "E",
    u"\u0119": "e",
    u"\u011A": "E",
    u"\u011B": "e",
    u"\u011C": "G",
    u"\u011D": "g",
    u"\u011E": "G",
    u"\u011F": "g",
    u"\u0120": "G",
    u"\u0121": "g",
    u"\u0122": "G",
    u"\u0123": "g",
    u"\u0124": "H",
    u"\u0125": "h",
    u"\u0128": "I",
    u"\u0129": "i",
    u"\u012A": "I",
    u"\u012B": "i",
    u"\u012C": "I",
    u"\u012D": "i",
    u"\u012E": "I",
    u"\u012F": "i",
    u"\u0130": "I",
    u"\u0131": "i",
    u"\u0132": "IJ",
    u"\u0133": "ij",
    u"\u0134": "J",
    u"\u0135": "j",
    u"\u0136": "K",
    u"\u0137": "k",
    u"\u0139": "L",
    u"\u013A": "l",
    u"\u013B": "L",
    u"\u013C": "l",
    u"\u013D": "L",
    u"\u013E": "l",
    u"\u0141": "L",
    u"\u0142": "l",
    u"\u0143": "N",
    u"\u0144": "n",
    u"\u0145": "N",
    u"\u0146": "n",
    u"\u0147": "N",
    u"\u0148": "n",
    u"\u0149": "n",
    u"\u014A": "NG",
    u"\u014B": "ng",
    u"\u014C": "O",
    u"\u014D": "o",
    u"\u014E": "O",
    u"\u014F": "o",
    u"\u0150": "O",
    u"\u0151": "o",
    u"\u0152": "OE",
    u"\u0153": "oe",
    u"\u0154": "R",
    u"\u0155": "r",
    u"\u0156": "R",
    u"\u0157": "r",
    u"\u0158": "R",
    u"\u0159": "r",
    u"\u015A": "S",
    u"\u015B": "s",
    u"\u015C": "S",
    u"\u015D": "s",
    u"\u015E": "S",
    u"\u015F": "s",
    u"\u0160": "S",
    u"\u0161": "s",
    u"\u0162": "T",
    u"\u0163": "t",
    u"\u0164": "T",
    u"\u0165": "t",
    u"\u0168": "U",
    u"\u0169": "u",
    u"\u016A": "U",
    u"\u016B": "u",
    u"\u016C": "U",
    u"\u016D": "u",
    u"\u016E": "U",
    u"\u016F": "u",
    u"\u0170": "U",
    u"\u0171": "u",
    u"\u0172": "U",
    u"\u0173": "u",
    u"\u0174": "W",
    u"\u0175": "w",
    u"\u0176": "Y",
    u"\u0177": "y",
    u"\u0178": "Y",
    u"\u0179": "Z",
    u"\u017A": "z",
    u"\u017B": "Z",
    u"\u017C": "z",
    u"\u017D": "Z",
    u"\u017E": "z",
    u"\u01F5": "g",
    u"\u03CC": "o",
    u"\u2013": "-",
    u"\u207b": "-",
    u"\u2014": "--",
    u"\u2015": "---",
    u"\u2018": "'",
    u"\u2019": "'",
    u"\u2032": "'",
    u"\xa0": " ",
}
try:
	translation_table = dict([(ord(k), unicode(v)) for k, v in unicode_to_latex.items()])
except NameError:
	translation_table = dict([(ord(k), str(v)) for k, v in unicode_to_latex.items()])

firstPrintInMaster = True

def parse_accents_str(string):
	"""needed to remove bad unicode characters that cannot printed well"""
	if string is not None and string is not "":
		string = string.translate(translation_table)
	return string

def writeToFile(text, filename, k, addComment = False):
	"""write to file with try/except to avoid problems with unicode"""
	global firstPrintInMaster
	try:
		if addComment and firstPrintInMaster:
			firstPrintInMaster = False
			with open(filename,"a") as stream:
				stream.write("%%lines added by bibtexImporter.py")
		with open(filename,"a") as stream:
			stream.write(text)
		return True
	except UnicodeEncodeError, e:
		print("the current entry '%s' cannot be saved since it contains a bad unicode character!"%m)
		print(e)
		return False

def retrieveurl(bibkey):
	"""search Inspires for the missing entries"""
	url="http://inspirehep.net/search?p=" + bibkey + "&sf=&so=d&rm=&rg=1000&sc=0&of=hx&em=B";
	print("looking for '%s' in %s"%(bibkey, url))
	response = urlopen(url)
	data = response.read()      # a `bytes` object
	text = data.decode('utf-8')
	i1=text.find("<pre>")
	i2=text.find("</pre>")
	if i1>0 and i2>0:
		text=text[i1+5:i2]
	else:
		text=""
	return text

#read which bib files are in the main folder
l=os.listdir(bibfolder)
bibs=[]
for e in l:
	if e.find('.bib')>0 and e.find('.bak')<0:
		bibs.append(e)

#read the folder name, scan it for the existing .tex files to be compiled
keysfold=sys.argv[1]
l=os.listdir(keysfold)
texs=[]
for e in l:
	if e.find('.tex')>0 and e.find('.bac')<0 and e.find('~')<0:
		texs.append(e)

#name of the output .bib file to be saved
outfile=sys.argv[2]

#print some information
print("reading keys from "+keysfold+" folder:")
print("    "+"    ".join(texs))
print("bib entries from "+bibfolder+" directory:")
print("    "+"    ".join(bibs))
print("saving in "+os.path.join(keysfold, outfile)+"\n")

if not os.path.isfile(os.path.join(keysfold, outfile)):
	with open(os.path.join(keysfold, outfile),'a'):
		os.utime(os.path.join(keysfold, outfile),None)

#save content of tex files in a string:
keyscont=""
for t in texs:
	with open(os.path.join(keysfold, t)) as r:
		keyscont += r.read()
#if existing, read output file (to detect which bibtex entries are already there:)
with open(os.path.join(keysfold, outfile)) as r:
	outcont = r.read()
#read the local bibtex database in the specified folder
allbib=""
for b in bibs:
	with open(os.path.join(bibfolder, b)) as r:
		allbib += r.read()
allbib+="@" #due to the way entries are parsed with regex...

#regular expression utilities
cite=re.compile('\\\\(cite|citep|citet)\{([A-Za-z]*:[0-9]*[a-z]*[,]?[\n ]*|[A-Za-z0-9\-][,]?[\n ]*)*\}',re.MULTILINE)	#find \cite{...}
bibel=re.compile('@[a-zA-Z]*\{(\s)*([A-Za-z]*:[0-9]*[a-z]*)?(\s)*,',re.MULTILINE|re.DOTALL)	#find the @Article(or other)...}, entry for the key "m"
bibty=re.compile('@[a-zA-Z]*\{',re.MULTILINE|re.DOTALL)	#find the @Article(or other) entry for the key "m"
#You can add here more fields that you have in your local bib file but that are not necessary for compilation:
unw1=re.compile('[ ]*(Owner|Timestamp|__markedentry|File)+[ ]*=.*?,[\n]*')	#remove unwanted fields
unw2=re.compile('[ ]*(Owner|Timestamp|__markedentry|File)+[ ]*=.*?[\n ]*\}')	#remove unwanted fields
unw3=re.compile('[ ]*Abstract[ ]*=[ ]*[{]+(.*?)[}]+,',re.MULTILINE)		#remove Abstract field

#use regex to detect "\cite{...}" commands in the tex files:
citaz=[m for m in cite.finditer(keyscont)]
strs=[]
#for each "\cite{...}", extract the cited bibtex keys
for c in citaz:
	b=c.group().replace(r'\cite{','').replace(r'\citep{', '').replace(r'\citet{', '')
	d=b.replace(' ','')
	b=d.replace('\n','')
	d=b.replace(r'}','')
	a=d.split(',')
	for e in a:
		if e not in strs:
			strs.append(e)
print("keys found: %d"%len(strs))

missing=[]
warnings=0
#read the list of needed bibtex keys and check which ones are already in the main bibliography files
for s in strs:
	if s not in outcont:
		missing.append(s)
print("missing: %d"%len(missing))

notfound=""
keychange=""
writeFailed=""
#enters the main loop. If entries exist locally, they are just copied, else INSPIRES will be searched for them
for m in missing:
	art=re.compile('@[a-zA-Z]*\{(\s)*'+m+'(\s)*,.*?@',re.MULTILINE|re.DOTALL)	#find the @Article(or other) entry for the key "m"
	t=[j for j in art.finditer(allbib)]
	#local bibtexs match: remove unwanted stuff and copy to output file
	if len(t)>0:
		a=t[0].group()
		bib='@'+a.replace('@','')
		for u in unw1.finditer(bib):
			bib=bib.replace(u.group(),'')
		for u in unw2.finditer(bib):
			bib=bib.replace(u.group(),'')
		for u in unw3.finditer(bib):
			bib=bib.replace(u.group(),'')
		bibf = '\n'.join([line for line in bib.split('\n') if line.strip() ])
		if writeToFile(bibf+"\n", os.path.join(keysfold, outfile), m):
			print("- %s inserted!"%m)
	#entry missing in local database: search inspires
	else:
		new=parse_accents_str(retrieveurl(m))#open search url
		currentSaveMaster=True
		currentSaveLocal=True
		if len(new):
			#sometimes inspires changes the bibtex keys after some time.
			#save the entry in the output .bib file and give a warning if it happened for the current entry
			if new.find(m)>0:
				if writeToFile(new+"\n",os.path.join(bibfolder, saveInFile),m, True):
					print("'%s' retrieved by InspireHEP and inserted into %s file - %d bytes"%(m,saveInFile,len(new)))
				else:
					currentSaveMaster=False
				if writeToFile(new+"\n",os.path.join(keysfold, outfile),m):
					print("...inserted in the %s file!"%outfile)
				else:
					currentSaveLocal=False
			else:
				warnings+=1
				t=[j.group() for j in bibel.finditer(new)]
				t1=[]
				for s in t:
					for u in bibty.finditer(s):
						s=s.replace(u.group(),'')
					s=s.replace(',','')
					t1.append(s)
				keychange+= "-->     WARNING! %s has a new key: %s\n"%(m,t1[0])
				#first, save the bibtex as it is in the main database or temporary file:
				for s in t1:
					if m not in allbib and str(s) not in allbib:
						if writeToFile(new+"\n",os.path.join(bibfolder, saveInFile),m, True):
							print("'%s' (new key '%s') retrieved by InspireHEP and inserted in the %s file - %d bytes"%(m,s,saveInFile,len(new)))
						else:
							currentSaveMaster=False
					if str(s) not in outcont:
						if writeToFile(new+"\n",os.path.join(keysfold, outfile),m):
							print("...inserted in the %s file!"%outfile)
						else:
							currentSaveLocal=False
			if not (currentSaveLocal and currentSaveMaster):
				warnings+=1
				print("----something wrong in adding '%s'!"%m)
				writeFailed+="-->     WARNING! %s cannot be saved! (bad unicode characters?)\n"%m
		else:
			notfound+="-- warning: missing entry for %s\n"%m
			warnings+=1
#print resume of what has been done: keys that don't exist in INSPIRES, entries whose key has been changed, total number of warnings
print("finished!\n")
print(notfound)
print(keychange)
print(writeFailed)
print("-->     %d warning(s) occurred!"%warnings)
