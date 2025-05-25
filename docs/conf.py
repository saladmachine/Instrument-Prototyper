# Configuration file for the Sphinx documentation builder.

import os
import sys
sys.path.insert(0, os.path.abspath('..'))  # Add project root to sys.path

project = 'Instrument-Prototyper'
copyright = '2025, saladmachine'
author = 'saladmachine'
release = '0.1.0'

# Sphinx extensions
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',   # For Google/NumPy style docstrings
    'sphinx.ext.viewcode',   # Adds links to highlighted source code
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# HTML output
html_theme = 'alabaster'  # Or 'sphinx_rtd_theme' if you prefer

# Napoleon settings (optional, but recommended)
napoleon_google_docstring = True
napoleon_numpy_docstring = True

# Autodoc settings (optional)
autoclass_content = 'both'     # Include both class docstring and __init__
autodoc_member_order = 'bysource'
autodoc_inherit_docstrings = True
