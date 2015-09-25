from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(
	name='ckanext-odvl',
	version=version,
	description="OpenData Vlaanderen CKAN Extension",
	long_description="""\
	""",
	classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
	keywords='',
	author='Philippe Duchesne',
	author_email='phd@highlatitud.es',
	url='ckan.be',  # TODO update with final URL
	license='',
	packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
	namespace_packages=['ckanext', 'ckanext.odvl'],
	include_package_data=True,
	zip_safe=False,
	install_requires=[
		# -*- Extra requirements: -*-
	],
	entry_points=\
	"""
        [ckan.plugins]
	# Add plugins here, eg
	odvl_extension=ckanext.odvl.plugin:ODVLExtension

	    [ckan.rdf.profiles]
    vl_dcat_ap=ckanext.odvl.profiles:VLDCATAPProfile
	""",
)
