# Configuration file for the Sphinx documentation builder.
import os
import sys
sys.path.insert(0, os.path.abspath('..'))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Speech Markdown'
copyright = '2026, Takeshi Teshima'
author = 'Takeshi Teshima'

version = '0.0.0'
release = '0.0.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'myst_parser',
    'sphinx_autodoc_typehints',
    'autoapi.extension',
]

autoapi_dirs = ['../speechmarkdown']
autoapi_type = "python"
autoapi_options = [
    'members',
    'undoc-members',
    'show-inheritance',
    'show-module-summary',
    'special-members',
    'imported-members',
]
autoapi_add_toctree_entry = True
autoapi_keep_files = True  # Keep files to inspect them
autoapi_template_dir = '_templates'
autoapi_python_use_implicit_namespaces = True

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_book_theme'
html_title = "Speech Markdown"
html_theme_options = {
    "repository_url": "https://github.com/speechmarkdown-py/speechmarkdown-py",
    "use_repository_button": True,
    "use_edit_page_button": True,
    "use_issues_button": True,
    "show_navbar_depth": 1,
    "navigation_depth": 10,
    "max_navbar_depth": 10,
}