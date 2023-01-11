"""
tests._templates
================
"""
COOKIECUTTER_JSON = """
{
  "author": "Stephen Whitlock",
  "github_username": "jshwi",
  "email": "stephen@jshwisolutions.com",
  "project_name": "project-name",
  "project_slug": "{{ cookiecutter.project_name|lower|replace('-', '_') }}",
  "project_version": "0.0.0",
  "project_description": "Short description for {{ cookiecutter.project_name }}",
  "project_keywords": "comma,separated,list",
  "include_entry_point": [
    "n",
    "y"
  ]
}
"""
