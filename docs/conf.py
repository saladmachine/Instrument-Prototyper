import os
import sys
sys.path.insert(0, os.path.abspath("../examples"))

project = "saladmachine"
author = "saladmachine"
release = "0.1"

extensions = ["sphinx.ext.autodoc", "sphinx.ext.napoleon"]
templates_path = ["_templates"]
exclude_patterns = []
html_theme = "alabaster"
