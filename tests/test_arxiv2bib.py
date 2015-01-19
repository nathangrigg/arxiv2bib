#! /usr/bin/env python

import arxiv2bib as a2b
import unittest
from mock import patch, Mock
from xml.etree import ElementTree
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

# provides fake data for 1001.1001v1 and 1205.1001v1
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
fakedata = patch('arxiv2bib.arxiv_request',
  return_value=ElementTree.fromstring(DATA))


class testArxivRequest(unittest.TestCase):
    @patch('arxiv2bib.urlopen', return_value=Mock(read=lambda:DATA))
    def test_arxiv_request_encode_url(self, mock_urlopen):
        output = a2b.arxiv_request(['a', 'b'])
        expected = 'http://export.arxiv.org/api/query?id_list=a%2Cb&max_results=2'
        mock_urlopen.assert_called_with(expected)

    @patch('arxiv2bib.urlopen', side_effect=a2b.HTTPError(None, 403, None, None, None))
    def test_catch_403_error(self, mock_uo):
        cli = a2b.Cli(['0000.0000'])
        self.assertRaises(a2b.FatalError, cli.run)

    @patch('arxiv2bib.urlopen')
    def test_no_unneccesary_API_call(self, mock_uo):
        cli = a2b.Cli(['x'])
        mock_uo.assert_not_called()

    @patch('arxiv2bib.urlopen', side_effect=a2b.HTTPError(None, 404, None, None, None))
    def test_catch_http_error(self, mock_uo):
        cli = a2b.Cli(['0000.0000'])
        self.assertRaises(a2b.FatalError, cli.run)


class testRegularExpressions(unittest.TestCase):
    def test_new_style_no_version(self):
        match = a2b.NEW_STYLE.match('1234.1234')
        self.assertTrue(match)

    def test_new_style_with_version(self):
        match = a2b.NEW_STYLE.match('1234.1234v1')
        self.assertTrue(match)

    def test_new_style_no_match(self):
        invalid = ['123456789', '1234.1234v']
        for x in invalid:
            match = a2b.NEW_STYLE.match(x)
            self.assertFalse(match, x)

    def test_longer_style_2015(self):
        match = a2b.NEW_STYLE.match('1501.03505')
        self.assertTrue(match)

    def test_old_style_no_subcategory(self):
        cats = ['physics', 'stat', 'hep-ph', 'math']
        for cat in cats:
            match = a2b.OLD_STYLE.match(cat + '/0000000')
            self.assertTrue(match, cat)

    def test_old_style_bad_subcategory(self):
        cats = ['physics', 'stat', 'hep-ph', 'math']
        for cat in cats:
            match = a2b.OLD_STYLE.match(cat + '.foo/0000000')
            self.assertFalse(match, cat)

    def test_old_style_good_subcategory(self):
        subcats = ['physics.atom-ph', 'math.CO', 'stat.TH']
        for sub in subcats:
            match = a2b.OLD_STYLE.match(sub + '/0000000')
            self.assertTrue(match, sub)

    def test_old_style_with_version(self):
        match = a2b.OLD_STYLE.match('physics.acc-ph/0000000v2')
        self.assertTrue(match)

    def test_is_valid_new_style(self):
        self.assertTrue(a2b.is_valid('0000.0000'))

    def test_is_valid_old_style(self):
        self.assertTrue(a2b.is_valid('math.CO/0000000'))

    def test_is_valid_return_false(self):
        self.assertFalse(a2b.is_valid('a'))


class testArxiv2Bib(unittest.TestCase):
    def setUp(self):
        fakedata.start()
        result = a2b.arxiv2bib(['1011.9999', '1001.1001v1', 'x', '1205.1001'])
        self.not_found, self.judge, self.invalid, self.frv = result

    def tearDown(self):
        fakedata.stop()

    def test_parse_single_author(self):
        self.assertEqual(self.judge.authors, ['Philip G. Judge'])

    def test_parse_multiple_authors(self):
        self.assertEqual(len(self.frv.authors), 3)
        self.assertEqual(self.frv.authors[0], 'Timo Fischer')

    def test_parse_category(self):
        self.assertEqual(self.frv.category, 'cond-mat.soft')

    def test_parse_id(self):
        self.assertEqual(self.frv.id, '1205.1001v1')

    def test_parse_bare_id(self):
        self.assertEqual(self.judge.bare_id, '1001.1001')

    def test_parse_published(self):
        self.assertEqual(self.frv.year, '2012')
        self.assertEqual(self.frv.month, 'May')

    def test_form_bibtex(self):
        self.assertEqual(self.frv.bibtex()[:21], '@article{1205.1001v1,')

    def test_reference_error_info(self):
        r = self.not_found
        self.assertEqual(type(r), a2b.ReferenceErrorInfo)
        self.assertEqual(r.message, 'Not found')
        self.assertEqual(r.id, '1011.9999')
        self.assertEqual(r.updated, '0')
        r = self.invalid
        self.assertEqual(type(r), a2b.ReferenceErrorInfo)
        self.assertEqual(r.message, 'Invalid arXiv identifier')
        self.assertEqual(r.id, 'x')
        self.assertEqual(r.updated, '0')


class testCLI(unittest.TestCase):
    def setUp(self):
        fakedata.start()
        self.vanilla = a2b.Cli(['1011.9999', '1001.1001v1', 'x'])
        self.vanilla.run()
        self.comments = a2b.Cli(['--comments', 'x'])
        self.comments.run()
        self.no_errors = a2b.Cli(['1001.1001'])
        self.no_errors.run()
        self.no_matches = a2b.Cli(['x'])
        self.no_matches.run()

    def tearDown(self):
        fakedata.stop()

    @patch('sys.stdin')
    def test_read_from_stdin(self, mock_in):
        mock_in.__iter__.return_value = ['1', '2']
        cli = a2b.Cli([])
        self.assertEqual(cli.args.id, ['1', '2'])

    def test_comment_output(self):
        expected = ['@comment{x: Invalid arXiv identifier}']
        self.assertEqual(expected, self.comments.output)

    def test_comment_argument_parsing(self):
        self.assertTrue(self.comments.args.quiet)

    def test_error_messages(self):
        expected = set(['Error: Not found (1011.9999)',
                        'Error: Invalid arXiv identifier (x)',
                        '1 of 3 matched succesfully'])
        actual = set(self.vanilla.messages)
        self.assertEqual(expected, actual)

    def test_output_messages(self):
        self.assertEqual(len(self.vanilla.output), 1)
        expected = '@article{1001.1001v1,\nAuthor        = {Philip G. Judge}'
        self.assertEqual(self.vanilla.output[0][:55], expected)

    def test_tally_errors(self):
        self.assertEqual(self.no_errors.code, 0)
        self.assertEqual(self.vanilla.code, 1)
        self.assertEqual(self.no_matches.code, 2)

    @patch('sys.stdout', new_callable=StringIO)
    def test_print_output_no_output(self, mock_out):
        self.no_matches.print_output()
        self.assertEqual(mock_out.getvalue(), "")

    @patch('sys.stdout', new_callable=StringIO)
    def test_print_output_with_output(self, mock_out):
        self.comments.print_output()
        expected = "@comment{x: Invalid arXiv identifier}"
        actual = mock_out.getvalue().rstrip()
        self.assertEqual(expected, actual)

    @patch('sys.stderr', new_callable=StringIO)
    def test_print_messages(self, mock_err):
        self.comments.print_messages()
        expected = "No successful matches"
        actual = mock_err.getvalue().rstrip()
        self.assertEqual(expected, actual)

    @patch('sys.stdout', new_callable=StringIO)
    @patch('sys.stderr', new_callable=StringIO)
    def test_main_function(self, mock_out, mock_err):
        code = a2b.main(['1001.1001', 'x'])
        self.assertEqual(code, 1)


    @patch('arxiv2bib.arxiv_request', side_effect=a2b.FatalError('xxx'))
    @patch('sys.stderr', new_callable=StringIO)
    def test_fatal_error_catch(self, mock_err, mock_connect):
        code = a2b.main(['1001.1001'])
        self.assertEqual(code, 2)
        self.assertEqual(mock_err.getvalue().strip(), 'xxx')
