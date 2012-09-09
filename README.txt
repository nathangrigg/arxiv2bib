Provides a command line tool to get metadata for an academic paper
posted at arXiv.org in BibTeX format.

Transform this::

    $ arxiv2bib 1001.1001

Into this::

    @article{1001.1001v1,
    Author        = {Philip G. Judge},
    Title         = {The chromosphere: gateway to the corona, or the purgatory of solar
      physics?},
    Eprint        = {1001.1001v1},
    ArchivePrefix = {arXiv},
    PrimaryClass  = {astro-ph.SR},
    Abstract      = {I argue that one should attempt to understand the solar chromosphere not only
    for its own sake, but also if one is interested in the physics of: the corona;
    astrophysical dynamos; space weather; partially ionized plasmas; heliospheric
    UV radiation; the transition region. I outline curious observations which I
    personally find puzzling and deserving of attention.},
    Year          = {2010},
    Month         = {Jan}
    }

Installation
------------



More Examples
-------------

Request a specific version::

    $ arxiv2bib.py 1102.0001v2

Request multiple papers at once::

    $ arxiv2bib.py 1101.0001 1102.0002 1103.0003

Use a list of papers from a text file (one per line)::

    $ arxiv2bib.py < papers.txt
