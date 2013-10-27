===================================================
ckanext-odvl - CKAN profile for OpenData Vlaanderen
===================================================

This extension defines one plugin to activate to apply the OpenData Vlaanderen (ODVL) theme and features:

* ODVLExtension (``odvl_extension``)

Installation
============
1. Install the extension into your python environment.

   *Note:* This extension is developed on CKAN 2.0.1 .

   For a production site, use the `stable` branch, unless there is a specific
   branch that targets the CKAN core version that you are using.

   To install the extension directly from github, use::

     (pyenv) $ pip install -e git+https://bitbucket.org/highlatitudes/ckanext-odvl.git#egg=ckanext-odvl

2. Make sure the CKAN configuration ini file contains the odvl main plugin::

    ckan.plugins = odvl_extension

UI Theme
--------
