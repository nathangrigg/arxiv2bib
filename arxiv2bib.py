#! /usr/bin/python

# By Nathan Grigg, Feb 2012
#
# Indiscriminate automated downloads from arXiv.org are not permitted.
# For more information, see http://arxiv.org/help/robots
#
# This script usually makes only one call to arxiv.org per run.
# No caching of any kind is performed.

from urllib import urlopen,urlencode
from xml.etree import ElementTree
import sys
import re

ATOM ='{http://www.w3.org/2005/Atom}'
ARXIV = '{http://arxiv.org/schemas/atom}'
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

class Error(Exception):
    pass

class Reference:
    """Represents a single reference, parses xml upon initialization."""
    def __init__(self,entry_xml,error="",id=""):
        if error:
            self._error(error,id)
        else:
            self.xml = entry_xml
            self.id = self._id()
            self.authors  = self._authors()
            self.title    = self._field_text('title')
            if len(self.id)==0 or len(self.authors)==0 or len(self.title)==0:
                self._error("No such publication",self.id)
            else:
                self.summary  = self._field_text('summary')
                self.category = self._category()
                self.year,self.month = self._published()
                self.updated = self._field_text('updated')
                self.bare_id = self.id[:self.id.rfind('v')]
                self.note = self._field_text('journal_ref',namespace=ARXIV)
                self.error = ""

    def _authors(self):
        """Extracts author names from xml."""
        xml_list = self.xml.findall(ATOM+'author/'+ATOM+'name')
        return [field.text for field in xml_list]

    def _field_text(self,id,namespace=ATOM):
        """Extracts text from arbitrary xml field"""
        try:
            return self.xml.find(namespace+id).text.strip()
        except:
            return ""

    def _category(self):
        try:
            return self.xml.find(ARXIV+'primary_category').attrib['term']
        except:
            return ""

    def _id(self):
        try:
            id_url=self._field_text('id')
            return id_url[id_url.find('/abs/')+5:]
        except:
            return ""

    def _published(self):
        published = self._field_text('published')
        if len(published) < 7:
            return "",""
        y,m = published[:4],published[5:7]
        try:
            m = ["Jan","Feb","Mar","Apr","May","Jun","Jul",
                 "Aug","Sep","Nov","Dec"][int(m)-1]
        except:
            pass
        return y,m

    def _error(self,error,id):
        """Initializes empty reference with error message."""
        self.error = error
        self.id = id
        self.bare_id = id
        self.authors=""
        self.title=""
        self.summary=""
        self.category=""
        self.year=""
        self.updated=""
        self.note=""

    def bibtex(self):
        """Returns BibTex string of the reference."""
        if self.error:
            return "@comment{%(id)s: %(error)s}" % \
                {'id': self.id, 'error': self.error}

        lines = ["@article{" + self.id ]
        for k,v in [("Author"," and ".join(self.authors)),
                    ("Title",self.title),
                    ("Eprint",self.id),
                    ("ArchivePrefix","arXiv"),
                    ("PrimaryClass",self.category),
                    ("Abstract",self.summary),
                    ("Year",self.year),
                    ("Month",self.month),
                    ("Note",self.note)]:
            if len(v):
                lines.append("%-13s = {%s}" % (k,v))

        return ",\n".join(lines) + "\n}"

def is_valid(id):
    """Checks if id is a valid arxiv identifier"""
    if NEW_STYLE.match(id) is not None or OLD_STYLE_XX.match(id) is not None:
        return True
    match = OLD_STYLE_PH.match(id)
    if match is not None and match.group(1) in physics_categories:
        if match.group(3) is None or \
        match.group(3) in physics_categories[match.group(1)]:
            return True
    return False


def arxiv2bib(id_list):
    """Returns a list of references, corresponding to elts of id_list"""
    d = arxiv2bib_dict(id_list)
    l = []
    for id in id_list:
        try:
            l.append(d[id])
        except:
            l.append(Reference(None,"Not found",id))

    return l

def arxiv_request(ids):
    """Sends a request to the arxiv API."""
    q = urlencode([
         ("id_list", ",".join(ids)),
         ("max_results", len(ids))
         ])
    url = "http://export.arxiv.org/api/query?" + q
    xml = urlopen(url)
    if xml.getcode() == 403:
        raise Error(
"""403 Forbidden error. This usually happens when you make many
rapid fire requests in a row. If you continue to do this, arXiv.org may
interpret your requests as a denial of service attack.

For more information, see http://arxiv.org/help/robots.
""")
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
            d[id]=Reference(None,error="Invalid arXiv identifier",id=id)

    if len(ids) == 0:
        return d

    # make the api call
    while True:
        xml = arxiv_request(ids)

        # check for error
        entries = xml.findall(ATOM+"entry")
        try:
            first_title = entries[0].find(ATOM+"title")
        except:
            raise Error("Unable to connect to arXiv.org API.")

        if first_title is None or first_title.text.strip() != "Error":
            break

        try:
            id = entries[0].find(ATOM+"summary").text.split()[-1]
            del(ids[ids.index(id)])
        except:
            raise Error("Unable to parse an error returned by arXiv.org.")


    # Parse each reference and store it in dictionary
    for entry in entries:
        ref = Reference(entry)
        if ref.id:
            d[ref.id] = ref
        if ref.bare_id:
            if not (ref.bare_id in d) or d[ref.bare_id].updated < ref.updated:
                d[ref.bare_id] = ref

    return d


# Main execution

if __name__ == "__main__":
    if '-h' in sys.argv or '--help' in sys.argv:
        print """Usage: %s [arxiv_id [arxiv_id [...]]]

Returns the BibTeX for each arXiv id.
If no arguments are given, it takes arXiv ids from stdin, one per line.

If only one id is given, it will print the BibTeX entry of the id, if possible.
Otherwise, it will return an error.

If multiple ids are given, it will print the BibTeX entry for each id, in the
order the ids were supplied. If it cannot find one particular id, it will
print an error message inside a BibTeX @comment field. It will return a
nonzero exit code if it cannot connect or fails to parse the arXiv api.
"""
        sys.exit(0)

    if len(sys.argv) == 1:
        id_list = [line.strip() for line in sys.stdin.readlines()]
    else:
        id_list = sys.argv[1:]

    try:
        bib = arxiv2bib(id_list)
    except Error as error:
        sys.exit(error)

    if len(bib) == 1 and bib[0].error:
        sys.exit(bib[0].error)
    else:
        for b in bib:
            print b.bibtex()

