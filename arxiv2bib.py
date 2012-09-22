#! /usr/bin/env python
#
# Copyright (c) 2012, Nathan Grigg
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
# * Neither the name of this package nor the
#   names of its contributors may be used to endorse or promote products
#   derived from this software without specific prior written permission.
#
# This software is provided by the copyright holders and contributors "as
# is" and any express or implied warranties, including, but not limited
# to, the implied warranties of merchantability and fitness for a
# particular purpose are disclaimed. In no event shall Nathan Grigg be
# liable for any direct, indirect, incidental, special, exemplary, or
# consequential damages (including, but not limited to, procurement of
# substitute goods or services; loss of use, data, or profits; or business
# interruption) however caused and on any theory of liability, whether in
# contract, strict liability, or tort (including negligence or otherwise)
# arising in any way out of the use of this software, even if advised of
# the possibility of such damage.
#
# (also known as the New BSD License)
#
# Indiscriminate automated downloads from arXiv.org are not permitted.
# For more information, see http://arxiv.org/help/robots
#
# This script usually makes only one call to arxiv.org per run.
# No caching of any kind is performed.

from urllib import urlencode
from urllib2 import HTTPError, urlopen
from xml.etree import ElementTree
import sys
import re
import os

if sys.version_info < (2, 6):
    raise Exception("Python 2.6 or higher required")

# Namespaces
ATOM ='{http://www.w3.org/2005/Atom}'
ARXIV = '{http://arxiv.org/schemas/atom}'

# regular expressions to check if arxiv id is valid
NEW_STYLE = re.compile(r'\d{4}\.\d{4}(v\d+)?$')
OLD_STYLE_XX = re.compile(
    r'(astro-ph)|(stat)|(q-fin)|(q-bio)|(cs)|(nlin)|(math)' +
    r'(\.[A-Z]{2})?/\d{7}(v\d+)?$')
physics_categories = {
    'cond-mat': ['dis-nn','mes-hall','mtrl-sci','other','quant-gas',
                 'soft','stat','str-el','supr-cond'],
    'gr-qc': [],
    'hep-ex': [],
    'hep-lat': [],
    'hep-ph': [],
    'hep-th': [],
    'nucl-ex': [],
    'nucl-th': [],
    'physics': ['acc-ph','ao-ph','atm-clus','atom-ph','bio-ph','chem-ph',
                'class-ph','comp-ph','data-an','ed-ph','flu-dyn','gen-ph',
                'geo-ph','hist-ph','ins-det','med-ph','optics','plasm-ph',
                'pop-ph','soc-ph','space-ph'],
    'quant-ph': []}
OLD_STYLE_PH = re.compile(r"([a-z\-]+)(\.([a-z\-]+))?/\d{7}(v\d+)?$")

def is_valid(id):
    """Checks if id resembles a valid arxiv identifier."""
    if NEW_STYLE.match(id) is not None or OLD_STYLE_XX.match(id) is not None:
        return True
    match = OLD_STYLE_PH.match(id)
    if match is not None and match.group(1) in physics_categories:
        if match.group(3) is None or \
        match.group(3) in physics_categories[match.group(1)]:
            return True
    return False

class FatalError(Exception):
    pass

class ReferenceError(Exception):
    pass

class Reference(object):
    """Represents a single reference.

    Instantiate using Reference(entry_xml). Note entry_xml should be
    an ElementTree.Element object.
    """
    def __init__(self, entry_xml):
        self.xml = entry_xml
        self.id = self._id()
        self.authors  = self._authors()
        self.title    = self._field_text('title')
        if len(self.id) == 0 or len(self.authors) == 0 or len(self.title) == 0:
            raise ReferenceError("No such publication", self.id)
        self.summary  = self._field_text('summary')
        self.category = self._category()
        self.year,self.month = self._published()
        self.updated = self._field_text('updated')
        self.bare_id = self.id[:self.id.rfind('v')]
        self.note = self._field_text('journal_ref', namespace=ARXIV)

    def _authors(self):
        """Extracts author names from xml."""
        xml_list = self.xml.findall(ATOM + 'author/' + ATOM + 'name')
        return [field.text for field in xml_list]

    def _field_text(self, id, namespace=ATOM):
        """Extracts text from arbitrary xml field"""
        try:
            return self.xml.find(namespace+id).text.strip()
        except:
            return ""

    def _category(self):
        """Get category"""
        try:
            return self.xml.find(ARXIV + 'primary_category').attrib['term']
        except:
            return ""

    def _id(self):
        """Get arxiv id"""
        try:
            id_url=self._field_text('id')
            return id_url[id_url.find('/abs/') + 5:]
        except:
            return ""

    def _published(self):
        """Get published date"""
        published = self._field_text('published')
        if len(published) < 7:
            return "", ""
        y,m = published[:4], published[5:7]
        try:
            m = ["Jan","Feb","Mar","Apr","May","Jun","Jul",
                 "Aug","Sep","Nov","Dec"][int(m)-1]
        except:
            pass
        return y, m

    def bibtex(self):
        """BibTex string of the reference."""

        lines = ["@article{" + self.id ]
        for k,v in [("Author", " and ".join(self.authors)),
                    ("Title", self.title),
                    ("Eprint", self.id),
                    ("ArchivePrefix", "arXiv"),
                    ("PrimaryClass", self.category),
                    ("Abstract", self.summary),
                    ("Year", self.year),
                    ("Month", self.month),
                    ("Note", self.note)]:
            if len(v):
                lines.append("%-13s = {%s}" % (k,v))

        return ("," + os.linesep).join(lines) + os.linesep + "}"

class ReferenceErrorInfo(object):
    """Contains information about a reference error"""
    def __init__(self, message, id):
        self.message = message
        self.id = id
        self.bare_id = id[:id.rfind('v')]
        # mark it as really old, so it gets superseded if possible
        self.updated = '0'

    def bibtex(self):
        """BibTeX comment explaining error"""
        return "@comment{%(id)s: %(message)s}" % \
                {'id': self.id, 'message': self.message}

    def __str__(self):
        return "Error: %(message)s (%(id)s)" % \
                {'id': self.id, 'message': self.message}

def arxiv2bib(id_list):
    """Returns a list of references, corresponding to elts of id_list"""
    d = arxiv2bib_dict(id_list)
    l = []
    for id in id_list:
        try:
            l.append(d[id])
        except:
            l.append(ReferenceErrorInfo("Not found", id))

    return l

def arxiv_request(ids):
    """Sends a request to the arxiv API."""
    q = urlencode([
         ("id_list", ",".join(ids)),
         ("max_results", len(ids))
         ])
    xml = urlopen("http://export.arxiv.org/api/query?" + q)
    # xml.read() returns bytes, but ElementTree.fromstring decodes
    # to unicode when needed (python2) or string (python3)
    return ElementTree.fromstring(xml.read())

def arxiv2bib_dict(id_list):
    """Fetches citations for ids in id_list into a dictionary indexed by id"""
    ids=[]
    d={}

    # validate ids
    for id in id_list:
        if is_valid(id):
            ids.append(id)
        else:
            d[id] = ReferenceErrorInfo("Invalid arXiv identifier", id)

    if len(ids) == 0:
        return d

    # make the api call
    while True:
        xml = arxiv_request(ids)

        # check for error
        entries = xml.findall(ATOM + "entry")
        try:
            first_title = entries[0].find(ATOM + "title")
        except:
            raise FatalError("Unable to connect to arXiv.org API.")

        if first_title is None or first_title.text.strip() != "Error":
            break

        try:
            id = entries[0].find(ATOM+"summary").text.split()[-1]
            del(ids[ids.index(id)])
        except:
            raise FatalError("Unable to parse an error returned by arXiv.org.")


    # Parse each reference and store it in dictionary
    for entry in entries:
        try:
            ref = Reference(entry)
        except ReferenceError as error:
            message, id = error.args
            ref = ReferenceErrorInfo(message, id)
        if ref.id:
            d[ref.id] = ref
        if ref.bare_id:
            if not (ref.bare_id in d) or d[ref.bare_id].updated < ref.updated:
                d[ref.bare_id] = ref

    return d

def parse_args():
    try:
        import argparse
    except:
        return("Cannot load required module 'argparse'")

    parser = argparse.ArgumentParser(
      description="Get the BibTeX for each arXiv id.",
      epilog="""\
Returns 0 on success, 1 on partial failure, 2 on total failure.
Valid BibTeX is written to stdout, error messages to stderr.
If no arguments are given, ids are read from stdin, one per line.""",
      formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('id',metavar='arxiv_id',nargs="*",
      help="arxiv identifier, such as 1201.1213")
    parser.add_argument('-c', '--comments', action='store_true',
      help="Include @comment fields with error details")
    parser.add_argument('-q', '--quiet', action='store_true',
      help="Display fewer error messages")
    parser.add_argument('-v', '--verbose', action="store_true",
      help="Display more error messages")
    return parser.parse_args()

def print_bytes(s):
    """Print bytes to stdout in Python 2 or 3"""
    if sys.version_info[0] == 2:
        sys.stdout.write(s)
    else:
        sys.stdout.buffer.write(s)

def main():
    args = parse_args()

    if len(args.id) == 0:
        id_list = [line.strip() for line in sys.stdin.readlines()]
    else:
        id_list = args.id

    # avoid duplicate error messages unless verbose is set
    if args.comments and not args.verbose:
        args.quiet = True

    try:
        bib = arxiv2bib(id_list)
    except HTTPError as error:
        if error.getcode() == 403:
            sys.stderr.write("""\
403 Forbidden error. This usually happens when you make many
rapid fire requests in a row. If you continue to do this, arXiv.org may
interpret your requests as a denial of service attack.

For more information, see http://arxiv.org/help/robots.
""")
        else:
            sys.stderr.write(
              "HTTP Connection Error: {0}".format(error.getcode()))
        return 2
    except FatalError as error:
        sys.stderr.write(error + os.linesep)
        return 2

    errors = 0
    output = []
    for b in bib:
        if type(b) is ReferenceErrorInfo:
            errors += 1
            if args.comments:
                output.append(b.bibtex())
            if not args.quiet:
                sys.stderr.write(str(b) + os.linesep)
        else:
            output.append(b.bibtex())

    # print it out
    output = os.linesep.join(output)
    if output:
        try:
            print output
        except UnicodeEncodeError:
            print_bytes((output + os.linesep).encode('utf-8'))
            if args.verbose:
                sys.stderr.write(
                  'Could not use system encoding; using utf-8' + os.linesep)

    # print error messages
    if errors == len(bib):
        sys.stderr.write("Error: No successful matches" + os.linesep)
        return 2
    elif errors > 0:
        sys.stderr.write("Error: %s of %s matched succesfully" % \
          (len(bib)-errors, len(bib)) + os.linesep)
        return 1

if __name__ == "__main__":
    sys.exit(main())
