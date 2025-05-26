# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os  # ADD THIS LINE
import sys  # ADD THIS LINE

# Update sys.path to tell Sphinx where to find your Python code files
sys.path.insert(0, os.path.abspath("../../src"))  # Path to your src/ directory
sys.path.insert(
    0, os.path.abspath("../../examples")
)  # Path to your examples/ directory


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Salad Machine"
copyright = "2025, Joe Pardue"
author = "Joe Pardue"
release = "1.0.0"  # Your release version, can be left blank or set as '1.0.0'


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# Add Sphinx extensions here.
# 'sphinx.ext.autodoc' automatically pulls documentation from docstrings.
# 'sphinx.ext.napoleon' allows Sphinx to understand Google/NumPy style docstrings (optional, but good to include).
# 'sphinx_rtd_theme' allows you to use the Read the Docs theme.
extensions = ["sphinx.ext.autodoc", "sphinx.ext.napoleon", "sphinx_rtd_theme"]

templates_path = ["_templates"]
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# Set the HTML theme to 'sphinx_rtd_theme' for a modern look.
html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

# Configuration for Napoleon (if using Google/NumPy style docstrings, otherwise it can be left out)
napoleon_google_docstring = True
napoleon_numpy_docstring = False
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

# Mock CircuitPython-specific modules so Sphinx can import the code without errors
autodoc_mock_imports = [
    "board",
    "digitalio",
    "busio",
    "sdcardio",
    "storage",
    "time",  # Though standard, sometimes helps avoid issues with CircuitPython time
    "os",  # Though standard, sometimes helps avoid issues with CircuitPython os
    "wifi",
    "socketpool",
    "secrets",
]
