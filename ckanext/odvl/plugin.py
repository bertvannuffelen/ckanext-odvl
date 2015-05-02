import os
import inspect
import ckan.plugins as p
import ckanext.odvl.helpers as helpers


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
        config['ckan.locale_order'] = config['ckan.locales_offered'] = 'nl fr de en'
        config['ckan.favicon'] = 'http://opendataforum.info/templates/tribune2/favicon.ico'
        #config['ckan.i18n_directory'] = 'theme';
        config['ckan.i18n_directory'] = os.path.join(os.path.dirname(inspect.getouterframes(inspect.currentframe())[0][1]),'theme')
        config['ckan.homepage_style'] = '-odvl'

        p.toolkit.add_template_directory(config, 'theme/templates')
        p.toolkit.add_public_directory(config, 'theme/public')
        p.toolkit.add_resource('theme/public', 'ckanext-odvl')

    @classmethod
    def example_helper(cls, data=None):
        # render our custom snippet
        return p.toolkit.render_snippet('custom_snippet.html', data)


    def get_helpers(self):
        return {
                'recent_updates': helpers.recent_updates,
                'top_publishers': helpers.top_publishers,
                'most_viewed_datasets': helpers.most_viewed_datasets,
                }