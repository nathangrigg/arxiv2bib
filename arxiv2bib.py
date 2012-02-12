#! /usr/bin/python


from urllib import urlopen,urlencode
from xml.etree import ElementTree
import sys

ATOM ='{http://www.w3.org/2005/Atom}'
ARXIV = '{http://arxiv.org/schemas/atom}'

class Reference:
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
                self.error = ""
    def _authors(self):
        xml_list = self.xml.findall(ATOM+'author/'+ATOM+'name')
        return [field.text for field in xml_list]

    def _field_text(self,id,namespace=ATOM):
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
            m = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Nov","Dec"][int(m)-1]
        except:
            pass
        return y,m

    def _error(self,error,id):
        self.error = error
        self.id = id
        self.bare_id = id
        self.authors=""
        self.title=""
        self.summary=""
        self.category=""
        self.year=""
        self.updated=""

    def bibtex(self):
        if self.error:
            return "@comment{%(id)s: %(error)s}" % \
                {'id': self.id, 'error': self.error}
        else:
            return """@article{%(id)s,
Author = {%(authors)s},
Title = {%(title)s},
Eprint = {%(id)s},
ArchivePrefix = {arXiv},
PrimaryClass = {%(class)s},
Abstract = {%(summary)s},
Year = {%(year)s},
Month = {%(month)s}
}""" % {'id':self.id, 'authors':" and ".join(self.authors),
                      'title':self.title, 'summary': self.summary,
                      'year':self.year,'month':self.month,'class':self.category}

def is_valid(id):
    """Checks if id is a valid arxiv identifier"""
    return True

def arxiv2bib(id_list):
    """Returns a list of bibtex strings, corresponding to elts of id_list"""
    d = arxiv2bib_dict(id_list)
    l = []
    for id in id_list:
        try:
            l.append(d[id])
        except:
            l.append(Reference(None,"Not found",id))

    return l

def arxiv_request(ids):
    q = urlencode([
                    ("id_list", ",".join(ids)),
                    ("max_results", len(ids))
                    ])
    url = "http://export.arxiv.org/api/query?" + q
    return ElementTree.fromstring(urlopen(url).read())

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

    # make the api call
    while True:
        xml = arxiv_request(ids)

        # check for error
        entries = xml.findall(ATOM+"entry")
        try:
            first_title = entries[0].find(ATOM+"title")
        except:
            sys.exit("Arxiv returning an error that I can't get around.")

        if first_title is None or first_title.text.strip() != "Error":
            break

        try:
            id = entries[0].find(ATOM+"summary").text.split()[-1]
            del(ids[ids.index(id)])
        except:
            sys.exit("Arxiv returning an error that I can't get around.")


    # Parse each reference and store it in dictionary
    for entry in entries:
        ref = Reference(entry)
        if ref.id:
            d[ref.id] = ref
        if ref.bare_id:
            if not (ref.bare_id in d) or d[ref.bare_id].updated < ref.updated:
                d[ref.bare_id] = ref

    return d

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
        sys.exit()

    if len(sys.argv) == 1:
        bib = arxiv2bib([line.strip() for line in sys.stdin.readlines()])
    else:
        bib = arxiv2bib(sys.argv[1:])

    if len(bib) == 1 and bib[0].error:
        sys.exit(bib[0].error)
    else:
        for b in bib:
            print b.bibtex()

