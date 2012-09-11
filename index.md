---
layout: default
---

# Arxiv2bib

Get arXiv.org metadata in BibTeX format

    $ arxiv2bib 1001.1001

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

# Installation 

Use [pip][1]:

    $ pip install arxiv2bib

Or use [easy_install][2]:

    $ easy_install arxiv2bib

Or download [the source][3] and use setup.py:

    $ python setup.py install

If you cannot install, you can use arxiv2bib.py as a standalone executable.

# Examples

Basic usage:

    $ arxiv2bib 1001.1001

Request a specific version:

    $ arxiv2bib 1102.0001v2

Request multiple papers at once:

    $ arxiv2bib 1101.0001 1102.0002 1103.0003

Use a list of papers from a text file (one per line):

    $ arxiv2bib < papers.txt

More information:

    $ arxiv2bib --help

# Documentation

## Basic usage

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

## arXiv identifiers

Identification numbers can be given as command line arguments (separated
by spaces) or via stdin (listed one per line). You may specify a specific
version of a paper (e.g. 1201.1213v2). If you do not specify the version
number, you will receive the information for the most recent version 
on the arXiv. You may also use old-style identification numbers when 
applicable (e.g. math.CO/0910323).

## Default operation

By default, the program prints the BibTeX for every paper it succesfully
locates via the arXiv API, in the order they were originally listed.
Papers which cannot be found are skipped. A warning is written to 
stderr for each skipped paper.

## The comments option

If the `--comments` option is given, error message are written in BibTeX
comment fields. This guarantees either an `@article` or `@comment` for
paper requested, in the same order as the request.

## Error codes

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

## Encoding

Standard BibTeX allows ASCII characters only, while the arXiv API uses
Unicode characters encoded by UTF-8.

Depending on which kind of TeX you use, you may need translate some 
non-ASCII characters to TeX commands (e.g. replace `é` with `\'e`)

The program will attempt to honor your local character encoding. If that is
not possible, it will encode as UTF-8.

## Requirements

Requires Python 2.6 or higher. If you are using Python 2.6, you will need
to also install the `argparse` module. In Python 2.7 or higher, 
this program has no dependencies.

The program will also work with Python 3, with installation via pip,
easy_install, or the included setup.py. You may also convert it manually
with 2to3.

[1]: http://www.pip-installer.org/en/latest/installing.html
[2]: http://pypi.python.org/pypi/setuptools
[3]: https://github.com/nathan11g/arxiv2bib/tarball/master

