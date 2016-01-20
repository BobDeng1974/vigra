#!/usr/bin/env python
from __future__ import division, print_function

import re
import glob
import sys

if len(sys.argv) != 3:
    print('usage: python post.py directory versionNumber')
    sys.exit(1)

path = str(sys.argv[1])

insertVersion = re.compile(r'VERSION_VERSION_VERSION')
insertSTLLink = re.compile(r'WWW_STL_DOCU')

# tested with doxygen 1.7.5.1
hasAnchorDetails = re.compile(r'<a (class="anchor" |)name="_?details"( id="details"|)>')

detailsHeading1 = re.compile(r'''<a name="_details"></a><h2>Detailed Description</h2>
<h3>''')

detailsHeading2 = re.compile(r'<a name="_details"></a><h2>Detailed Description</h2>')

# tested with doxygen 1.7.5.1 and 1.8.2
detailsHeading3 = re.compile(r'<a name="details" id="details"></a><h2( class="groupheader"|)>Detailed Description</h2>')

mainHeading1 = re.compile(r'''(<!-- Generated by Doxygen \d+\.\d+\.\d+ -->)
(  <div class="navpath">.*
  </div>
|)<div class="contents">
<h1>(.*)( Class Template Reference| Struct Template Reference| Class Reference| Struct Reference)(<br>
<small>
.*</small>
|)</h1>''')

mainHeading2 = re.compile(r'''(<!-- Generated by Doxygen \d+\.\d+\.\d+ -->)
(  <div class="navpath">.*
  </div>
<div class="contents">
|<div class="contents">
|)<h1>(.*)()(<br>
<small>
.*</small>
|)</h1>''')

# tested with doxygen 1.5.6
mainHeading3 = re.compile(r'''(<!-- Generated by Doxygen \d+\.\d+\.\d+ -->)
(<div class="header">
  <div class="headertitle">
)<h1>(.*)</h1>(.*)()
</div>
<div class="contents">''')

# tested with doxygen 1.7.5.1 and 1.7.6.1
mainHeading4 = re.compile(r'''(<!-- Generated by Doxygen .+ -->
</div>)
(<div class="header">
  <div class="headertitle">
)<div class="title">(.*)</div>  </div>(.*)()
</div>(?:<!--header-->)?
<div class="contents">''')

# tested with doxygen 1.8.2
mainHeading5 = re.compile(r'''(<!-- Generated by Doxygen .+ -->
</div><!-- top -->)
(<div class="header">
  <div class="headertitle">
)<div class="title">(.*)</div>  </div>(.*)()
</div>(?:<!--header-->)?
<div class="contents">''')


mainHeadingReplacement = '''\\1
<div class="contents">
<table class="main_heading">
<tr>
%s<td width="100%%">\\3\\5
</td>
<td align=right><a href="http://hci.iwr.uni-heidelberg.de/vigra/"><IMG border=0 ALT="VIGRA" SRC="documents/vigra.gif" title="VIGRA Homepage"></a></td></tr>
</table><p>
'''

# tested with doxygen 1.7.5.1
headingSummary = re.compile(r'''(<!-- Generated by Doxygen .+ -->
</div>
<div class="header">)
  <div class="summary">
(?s).*?</div>''')

# tested with doxygen 1.8.2
headingSummary2 = re.compile(r'''(<!-- Generated by Doxygen .+ -->
</div><!-- top -->
<div class="header">)
  <div class="summary">
(?s).*?</div>''')

# tested with doxygen 1.7.5.1
headingNavpath = re.compile(r'''(<!-- Generated by Doxygen .+ -->)
  <div id="nav-path" class="navpath">(?s).*?</div>''')

# tested with doxygen 1.8.2
headingNavpath2 = re.compile(r'''(<!-- Generated by Doxygen .+ -->)
<div id="nav-path" class="navpath">
  <ul>
.*  </ul>
</div>''')

detailsLink = '''<td align=left>
<A HREF ="#_details" ><IMG BORDER=0 ALT="details" title="Detailed Description" SRC="documents/pfeilGross.gif"></A>
</td>
'''

indexPageHeading = re.compile(r'''((?:<p>)?<a class="anchor" (?:name|id)="_details"></a> (?:</p>\n)?<center> </center>)<h2>(<a class="anchor" (?:name|id)="Main">(?:</a>)?)
(.*)
<center> Version''')

indexPageHeadingReplacement = '''\\1 <h2 class="details_section">\\2
\\3
<center> Version'''

templateDeclaration = re.compile('''<tr><td class="memTemplParams" nowrap colspan="2">([^<]*)</td></tr>\s*
<tr><td class="memTemplItemLeft" nowrap align="right" valign="top">[^<]*</td><td class="memTemplItemRight" valign="bottom"><a class="el" href=".*#([^"]+)">''')

templateDocumentation = '''(<a class="anchor" name="%s"></a>.*
<div class="memitem">
<div class="memproto">\s*
      <table class="memname">
        <tr>)'''

templateDocumentationReplacement = '''\\1
          <td colspan="4" class="memtemplate">%s</td></tr><tr>'''

def convertHeadings(text):
    if hasAnchorDetails.search(text):
        text = detailsHeading1.sub('<a name="_details"></a><h2 class="details_section">Detailed Description</h2>\n<h3 class="details_section">', \
                      text, 1)
        text = detailsHeading2.sub(r'<a name="_details"></a><h2 class="details_section">Detailed Description</h2>', text, 1)
        text = detailsHeading3.sub(r'<a name="_details" id="details"></a><h2 class="details_section">Detailed Description</h2>', text, 1)
        mhr = mainHeadingReplacement % detailsLink
    else:
        mhr = mainHeadingReplacement % ''
    text = headingNavpath.sub("\\1", text, 1)
    text = headingNavpath2.sub("\\1", text, 1)
    text = headingSummary.sub("\\1", text, 1)
    text = headingSummary2.sub("\\1", text, 1)
    text = mainHeading1.sub(mhr, text, 1)
    text = mainHeading2.sub(mhr, text, 1)
    text = mainHeading3.sub(mhr, text, 1)
    text = mainHeading4.sub(mhr, text, 1)
    text = mainHeading5.sub(mhr, text, 1)
    return text

def insertMissingTemplateDeclarations(text):
    matches = templateDeclaration.findall(text)
    for k in matches:
        text = re.sub(templateDocumentation % k[1], templateDocumentationReplacement % k[0], text)
    return text

def processFile(fileName):
    print(fileName)         # log message
    f = open(fileName)
    text = f.read()
    f.close()
    
    text = insertVersion.sub(sys.argv[2], text)
    text = insertSTLLink.sub(r'http://www.sgi.com/tech/stl/', text)
    if re.search('.*/index.html', fileName) or re.search('.*\\index.html', fileName):
        text = re.sub(r'<h3 (align="center"|class="version")>\d+\.\d+\.\d+ </h3>', '', text)
        text = indexPageHeading.sub(indexPageHeadingReplacement, text)
        
    text = convertHeadings(text)
    
    text = insertMissingTemplateDeclarations(text)

    f = open(fileName, 'w+')
    f.write(text)
    f.close()

files = glob.glob(path + '/*.html')  # use given path to files
#files = glob.glob(path + '/index.html')

for file in files:
   processFile(file)

