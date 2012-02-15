`arxiv2bib` uses the arxiv.org api to download a BibTeX entry for
a paper posted at <http://arxiv.org>.

# Examples

    $ arxiv2bib.py 1202.1023

    $ arxiv2bib.py 1102.0001v2

    $ arxiv2bib.py 1101.0001 1102.0002 1103.0003

Or, if you have a list of arxiv.org ids stored in `papers.txt`, one per line:

    $ arxiv2bib.py < papers.txt
