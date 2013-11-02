import os
import ckan.plugins as p


class ODVLExtension(p.SingletonPlugin):
    p.implements(p.IConfigurer, inherit=True)
    p.implements(p.ITemplateHelpers)

    def update_config(self, config):

        #config['ckan.site_logo'] = '/images/logo04.gif'
        #config['ckan.site_intro_text'] = 'test intro'
        # Defining and hiding the spatial extra field
        config['ckan.extra_resource_fields'] = 'spatial'
        config['package_hide_extras'] = 'spatial'
        config['search.facets'] = 'groups tags res_format'
        config['ckan.locale_default'] = 'nl'
        config['ckan.locale_order'] = 'nl fr de en'
        config['ckan.favicon'] = 'http://www.vlaanderen.be/sites/all/themes/portal/favicon.ico'

        p.toolkit.add_template_directory(config, 'theme/templates')
        p.toolkit.add_public_directory(config, 'theme/public')
        p.toolkit.add_resource('theme/public', 'ckanext-odvl')

    @classmethod
    def example_helper(cls, data=None):
        # render our custom snippet
        return p.toolkit.render_snippet('custom_snippet.html', data)


    def get_helpers(self):
        # register our helper function
        return {'example_helper': self.example_helper}