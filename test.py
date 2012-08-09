#! /usr/bin/env python

# makes 1 call to the api

import arxiv2bib as a2b
from unittest import TestCase, main
import zlib, base64

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
        self.xml = zlib.decompress(base64.decodestring(DATA))
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

DATA = """
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
r9Q="""


if __name__ == "__main__":
    main()


# arxiv2bib_dict: get it to throw the two fatalerrors,
#see if you can come up with something that loops, test the
#updated thing by sending a request for two versions of the same paper
#
# Reference: parse a couple, get it to throw the error.


