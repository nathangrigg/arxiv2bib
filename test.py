#! /usr/bin/env python

# makes 1 call to the api

import arxiv2bib as a2b
from unittest import TestCase, main

class testValidityCheck(TestCase):
    def test_new_style(self):
        self.assertTrue(a2b.is_valid("1203.1230"))
        self.assertTrue(a2b.is_valid("1012.1230v3"))
        self.assertTrue(a2b.is_valid("1301.1230v199"))
        self.assertFalse(a2b.is_valid("1111.1111v"))
    def test_old_style(self):
        valid = ["math/0409434", "astro-ph/0302530", "quant-ph/0612147",
          "hep-th/0612093", "cs/0612047", "hep-ph/0610206",
          "physics.space-ph/0123154", "cond-mat.stat/1021324"]
        for v in valid: self.assertTrue(a2b.is_valid(v))
        self.assertFalse(a2b.is_valid('math./1212121'))

class testArxiv2Bib(TestCase):
    def test_actual_request(self):
        res = a2b.arxiv2bib(['1011.9999', '1001.1001v1', 'x'])
        self.assertEqual(len(res), 3)

        r = res[0]
        self.assertEqual(type(r), a2b.ReferenceErrorInfo)
        self.assertEqual(r.message, 'Not found')
        self.assertEqual(r.id, '1011.9999')
        self.assertEqual(r.updated, '0')

        r = res[1]
        self.assertEqual(type(r), a2b.Reference)
        self.assertEqual(r.year, '2010')
        self.assertEqual(r.id, '1001.1001v1')

        r = res[2]
        self.assertEqual(type(r), a2b.ReferenceErrorInfo)
        self.assertEqual(r.message, 'Invalid arXiv identifier')
        self.assertEqual(r.id, 'x')
        self.assertEqual(r.updated, '0')

class testParsing(TestCase):
    def setUp(self):
        self.xml = DATA
        self.refs = a2b.ElementTree.fromstring(self.xml).findall(a2b.ATOM + "entry")
    def test_parse_first_entry(self):
        self.assertTrue(len(self.refs) >= 1)
        ref = a2b.Reference(self.refs[0])
        data = [ref.id, ref.authors, ref.title[:26], ref.summary[:33],
          ref.category, ref.year, ref.month, ref.updated, ref.bare_id, ref.note]
        should_match = ['1205.1001v1',
          ['Timo Fischer', 'H. Jelger Risselada', 'Richard L. C. Vink'],
           'Membrane lateral structure', 'In experiments on model membranes',
           'cond-mat.soft', '2012', 'May',
           '2012-05-04T16:23:05Z', '1205.1001', '']
        self.assertEqual(data, should_match)
        self.assertEqual(ref.bibtex()[:21], '@article{1205.1001v1,')

DATA = """<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <link href="http://arxiv.org/api/query?search_query%3D%26id_list%3D1205.1001v1%2C1001.1001v1%26start%3D0%26max_results%3D10" rel="self" type="application/atom+xml"/>
  <title type="html">ArXiv Query: search_query=&amp;id_list=1205.1001v1,1001.1001v1&amp;start=0&amp;max_results=10</title>
  <id>http://arxiv.org/api/NkeXEv4rDF4SylztF53oHCI2fdo</id>
  <updated>2012-08-09T00:00:00-04:00</updated>
  <opensearch:totalResults xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/">2</opensearch:totalResults>
  <opensearch:startIndex xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/">0</opensearch:startIndex>
  <opensearch:itemsPerPage xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/">10</opensearch:itemsPerPage>
  <entry>
    <id>http://arxiv.org/abs/1205.1001v1</id>
    <updated>2012-05-04T16:23:05Z</updated>
    <published>2012-05-04T16:23:05Z</published>
    <title>Membrane lateral structure: The influence of immobilized particles on
  domain size</title>
    <summary>  In experiments on model membranes, a formation of large domains of different
lipid composition is readily observed. However, no such phase separation is
observed in the membranes of intact cells. Instead, a structure of small
transient inhomogeneities called lipid rafts are expected in these systems. One
of the numerous attempts to explain small domains refers to the coupling of the
membrane to its surroundings, which leads to the immobilization of some of the
membrane molecules. These immobilized molecules then act as static obstacles
for the remaining mobile ones. We present detailed Molecular Dynamics
simulations demonstrating that this can indeed account for small domains. This
confirms previous Monte Carlo studies based on simplified models. Furthermore,
by directly comparing domain structures obtained using Molecular Dynamics to
Monte Carlo simulations of the Ising model, we demonstrate that domain
formation in the presence of obstacles is remarkably insensitive to the details
of the molecular interactions.
</summary>
    <author>
      <name>Timo Fischer</name>
    </author>
    <author>
      <name>H. Jelger Risselada</name>
    </author>
    <author>
      <name>Richard L. C. Vink</name>
    </author>
    <arxiv:comment xmlns:arxiv="http://arxiv.org/schemas/atom">submitted to PCCP</arxiv:comment>
    <link href="http://arxiv.org/abs/1205.1001v1" rel="alternate" type="text/html"/>
    <link title="pdf" href="http://arxiv.org/pdf/1205.1001v1" rel="related" type="application/pdf"/>
    <arxiv:primary_category xmlns:arxiv="http://arxiv.org/schemas/atom" term="cond-mat.soft" scheme="http://arxiv.org/schemas/atom"/>
    <category term="cond-mat.soft" scheme="http://arxiv.org/schemas/atom"/>
    <category term="physics.bio-ph" scheme="http://arxiv.org/schemas/atom"/>
  </entry>
  <entry>
    <id>http://arxiv.org/abs/1001.1001v1</id>
    <updated>2010-01-06T22:12:29Z</updated>
    <published>2010-01-06T22:12:29Z</published>
    <title>The chromosphere: gateway to the corona, or the purgatory of solar
  physics?</title>
    <summary>  I argue that one should attempt to understand the solar chromosphere not only
for its own sake, but also if one is interested in the physics of: the corona;
astrophysical dynamos; space weather; partially ionized plasmas; heliospheric
UV radiation; the transition region. I outline curious observations which I
personally find puzzling and deserving of attention.
</summary>
    <author>
      <name>Philip G. Judge</name>
    </author>
    <arxiv:comment xmlns:arxiv="http://arxiv.org/schemas/atom">To appear in the proceedings of the 25th NSO Workshop "Chromospheric
  Structure and Dynamics. From Old Wisdom to New Insights", Memorie della
  Societa' Astronomica Italiana, Eds. Tritschler et al</arxiv:comment>
    <link href="http://arxiv.org/abs/1001.1001v1" rel="alternate" type="text/html"/>
    <link title="pdf" href="http://arxiv.org/pdf/1001.1001v1" rel="related" type="application/pdf"/>
    <arxiv:primary_category xmlns:arxiv="http://arxiv.org/schemas/atom" term="astro-ph.SR" scheme="http://arxiv.org/schemas/atom"/>
    <category term="astro-ph.SR" scheme="http://arxiv.org/schemas/atom"/>
  </entry>
</feed>
"""

if __name__ == "__main__":
    main()


# arxiv2bib_dict: get it to throw the two fatalerrors,
#see if you can come up with something that loops, test the
#updated thing by sending a request for two versions of the same paper
#
# Reference: parse a couple, get it to throw the error.


