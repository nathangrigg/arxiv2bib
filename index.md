---
layout: default
---


Get arXiv.org metadata in BibTeX format

    $ arxiv2bib 1001.1001

    @article{1001.1001v1,
    Author        = {Philip G. Judge},
    Title         = {The chromosphere: gateway to the corona, or
        the purgatory of solar physics?},
    Eprint        = {1001.1001v1},
    ArchivePrefix = {arXiv},
    PrimaryClass  = {astro-ph.SR},
    Abstract      = {I outline curious observations which I
        personally find puzzling and deserving of attention.},
    Year          = {2010},
    Month         = {Jan}
    }

## Installation

Use [pip][1]:

    $ pip install arxiv2bib

Or use [easy_install][2]:

    $ easy_install arxiv2bib

Or download [the source][3] and use setup.py:

    $ cd Downloads/arxiv2bib
    $ python setup.py install

If you cannot install, you can use `arxiv2bib.py` as a standalone executable.

## Examples

Get the BibTeX for a single paper:

    $ arxiv2bib 1001.1001

Request a specific version:

    $ arxiv2bib 1102.0001v2

Request multiple papers at once:

    $ arxiv2bib 1101.0001 1102.0002 1103.0003

Use a list of papers from a text file (one per line):

    $ arxiv2bib < papers.txt

More information:

    $ arxiv2bib --help

## Documentation

### Help

    arxiv2bib [-h] [-c] [-q] [-v] [arxiv_id [arxiv_id ...]]

    Get the BibTeX for each arXiv id.

    positional arguments:
      arxiv_id        arxiv identifier, such as 1201.1213

    optional arguments:
      -h, --help      show this help message and exit
      -c, --comments  Include @comment fields with error details
      -q, --quiet     Display fewer error messages
      -v, --verbose   Display more error messages

    Returns 0 on success, 1 on partial failure, 2 on total failure.
    Valid BibTeX is written to stdout, error messages to stderr.
    If no arguments are given, ids are read from stdin, one per line.

### arXiv identifiers

Identification numbers can be given as command line arguments (separated
by spaces) or via stdin (listed one per line). You may specify a specific
version of a paper (e.g. `1201.1213v2`). If you do not specify the version
number, you will receive the information for the most recent version
on the arXiv. You may also use old-style identification numbers when
applicable (e.g. `math.CO/0910323`).

### Default operation

By default, the program outputs the BibTeX for every paper it succesfully
locates via the arXiv API, in the order they were originally listed.
Papers which cannot be found are skipped. A warning is written to
stderr for each skipped paper.

### Limit API calls

The program will generally make a single call to the arXiv API per run,
even if you request hundreds of papers.

If you run the program repeatedly (for example, in a for loop), you will
make repeated calls to the API, putting strain on the arXiv server.
If this becomes a problem, the API may block your IP address.
For more information, see <http://arxiv.org/help/robots>.

### The comments option

If the `--comments` option is given, error message are written in BibTeX
comment fields. This guarantees either an `@article` or `@comment` for
each paper requested, in the same order as the request.

### Interpreting error codes

If the program finds a matching paper for each identification number listed,
it returns a code of 0 (SUCCESS).

If the program finds at least one paper, but not every paper listed,
it returns a code of 1 (PARTIAL FAILURE).

If the program cannot find any papers, it returns a code of 2 (TOTAL FAILURE).
The program makes some attempt to eliminate invalid identification numbers
to prevent total failure when possible, but sometimes a bad identifier
will prevent the API from returning results, even though the other identifiers
are correct.

In every case, nothing is written to stdout that is not BiBTeX.

### Character encoding

Standard BibTeX allows ASCII characters only, while the arXiv API uses
Unicode characters encoded by UTF-8.

Depending on which kind of TeX you use, you may need translate some
non-ASCII characters to TeX commands (e.g. replace `é` with `\'e`)

The program will attempt to honor your local character encoding. If that is
not possible, it will encode as UTF-8.

### Python and system requirements

Works with Python 2.7 or higher and has no dependencies. Also runs on
Python 2.6, but you will need to install the
`argparse` module.

The program will also run on Python 3, with installation via pip,
easy_install, or the included setup.py. You can also convert it manually
with 2to3.

### License

Published under the new BSD license.


[1]: http://www.pip-installer.org/en/latest/installing.html
[2]: http://pypi.python.org/pypi/setuptools
[3]: https://github.com/nathangrigg/arxiv2bib/tarball/master
