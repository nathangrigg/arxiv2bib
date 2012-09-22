"""\
Provides a command line tool to get metadata for an academic paper
posted at arXiv.org in BibTeX format.

Transform this::

    $ arxiv2bib 1001.1001

Into this::

    @article{1001.1001v1,
    Author        = {Philip G. Judge},
    Title         = {The chromosphere: gateway to the corona,
      or the purgatory of solar physics?},
    Eprint        = {1001.1001v1},
    ArchivePrefix = {arXiv},
    PrimaryClass  = {astro-ph.SR},
    Abstract      = {I outline curious observations which I personally
    find puzzling and deserving of attention.},
    Year          = {2010},
    Month         = {Jan}
    }
"""

import sys
try: from setuptools import setup
except ImportError: sys.exit("""Error: Setuptools is required for installation.
 -> http://pypi.python.org/pypi/setuptools
 or http://pypi.python.org/pypi/distribute""")

extra = {}
if sys.version_info >= (3,):
    extra['use_2to3'] = True

setup(
    name = "arxiv2bib",
    version = "1.0.1",
    description = "Get arXiv.org metadata in BibTeX format",
    author = "Nathan Grigg",
    author_email = "nathan@nathanamy.org",
    url = "http://nathan11g.github.com/arxiv2bib",
    py_modules = ["arxiv2bib"],
    keywords = ["arxiv", "bibtex", "latex", "citation"],
    entry_points = {
        'console_scripts': ['arxiv2bib = arxiv2bib:main']
    },
    test_suite = 'test',
    license = "BSD",
    classifiers = [
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Topic :: Text Processing :: Markup :: LaTeX",
        "Environment :: Console"
        ],
    long_description = __doc__,
    **extra
)
