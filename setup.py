from distutils.core import setup
import arxiv2bib

setup(
    name = "arxiv2bib",
    version = arxiv2bib.__version__,
    description = "Get arXiv.org metadata in BibTeX format",
    author = "Nathan Grigg",
    author_email = "nathan@nathanamy.org",
    url = "http://nathan11g.github.com/arxiv2bib",
    py_modules = ["arxiv2bib"],
    keywords = ["arxiv", "bibtex", "latex", "citation"],
    scripts = ['scripts/arxiv2bib'],
    license = "BSD",
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Text Processing :: Markup :: LaTeX",
        "Environment :: Console"
        ],
    long_description = """\
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
""")
