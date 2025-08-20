# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------
import os
import sys
sys.path.insert(0, os.path.abspath('../src'))

# -- Project information -----------------------------------------------------
project = 'Scraper V4'
copyright = '2025, Masodori'
author = 'Masodori'
release = '4.1.1'
version = '4.1'

# -- General configuration ---------------------------------------------------
extensions = [
    'myst_parser',
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx_copybutton',
    'sphinx.ext.intersphinx',
    'sphinx.ext.autosummary',
    'sphinx.ext.todo',
]

# MyST Parser configuration
myst_enable_extensions = [
    "deflist",
    "tasklist", 
    "fieldlist",
    "colon_fence",
    "html_admonition",
    "linkify",
    "replacements",
    "smartquotes",
    "substitution",
    "tasklist",
]

# MyST configuration options
myst_heading_anchors = 3
myst_html_meta = {
    "description lang=en": "Scraper V4 - Advanced web scraping framework",
    "keywords": "web scraping, python, playwright, automation",
}

templates_path = ['_templates']
exclude_patterns = [
    '_build', 
    'Thumbs.db', 
    '.DS_Store',
    'build',
    'source',
    '**.ipynb_checkpoints'
]

# Source file suffixes
source_suffix = ['.rst', '.md']

# Master document
master_doc = 'index'
root_doc = 'index'

# Language
language = 'en'

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# Theme options
html_theme_options = {
    'analytics_id': '',
    'analytics_anonymize_ip': False,
    'logo_only': False,
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': False,
    'vcs_pageview_mode': '',
    'style_nav_header_background': '#2980B9',
    # Toc options
    'collapse_navigation': False,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False
}

# Custom CSS
html_css_files = []

# HTML context
html_context = {
    "display_github": True,
    "github_user": "masodori",
    "github_repo": "ScraperV4",
    "github_version": "main",
    "conf_py_path": "/docs/",
}

# -- Extension configuration -------------------------------------------------

# Intersphinx mapping
intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'requests': ('https://docs.python-requests.org/en/latest/', None),
    'pandas': ('https://pandas.pydata.org/docs/', None),
}

# Copy button configuration
copybutton_prompt_text = r">>> |\.\.\. |\$ |In \[\d*\]: | {2,5}\.\.\.: | {5,8}: "
copybutton_prompt_is_regexp = True
copybutton_exclude = '.linenos, .gp, .go'

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = True

# Todo extension configuration
todo_include_todos = True

# Autosummary settings
autosummary_generate = True

# -- Options for LaTeX output ------------------------------------------------
latex_elements = {
    'papersize': 'letterpaper',
    'pointsize': '10pt',
    'preamble': '',
    'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files
latex_documents = [
    (master_doc, 'ScraperV4.tex', 'Scraper V4 Documentation',
     'Masodori', 'manual'),
]

# -- Options for manual page output ------------------------------------------
man_pages = [
    (master_doc, 'scraperv4', 'Scraper V4 Documentation',
     [author], 1)
]

# -- Options for Texinfo output ----------------------------------------------
texinfo_documents = [
    (master_doc, 'ScraperV4', 'Scraper V4 Documentation',
     author, 'ScraperV4', 'Advanced web scraping framework.',
     'Miscellaneous'),
]

# -- Options for Epub output -------------------------------------------------
epub_title = project
epub_exclude_files = ['search.html']