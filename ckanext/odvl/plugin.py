import os
import inspect
import ckan.plugins as p
import ckanext.odvl.helpers as helpers
import ckan.logic as logic
import ckan.new_authz as new_authz
import ckan.lib.dictization.model_dictize as model_dictize
from ckan import model


@logic.side_effect_free
def members_of_orgs(context, data_dict=None):

    model = context['model']
    user = context['user']

    #logic.check_access('members_of_orgs', context, data_dict)
    sysadmin = new_authz.is_sysadmin(user)

    if sysadmin:
        users = model.Session.query(model.User) \
            .filter(model.User.state == 'active')

        members = model.Session.query(model.Member) \
            .filter(model.Member.table_name == 'user') \
            .filter(model.Member.capacity.isnot(None)) \
            .filter(model.Member.state == 'active')

        user_list = []

        for user in users.all():
            members = model.Session.query(model.Member) \
                .filter(model.Member.table_name == 'user') \
                .filter(model.Member.capacity.isnot(None)) \
                .filter(model.Member.table_id == user.id) \
                .filter(model.Member.state == 'active').all()
            if (len(members)>0):
                user_dict = {
                    'name' : user.name,
                    'fullname' : user.fullname,
                    'email' : user.email}
                user_dict['orgs'] = []
                for role in members:
                    org = model.Session.query(model.Group.name)\
                        .filter(model.Group.is_organization == True) \
                        .filter(model.Group.id == role.group_id) \
                        .filter(model.Group.state == 'active')\
                        .first()
                    user_dict['orgs'].append(
                        {'role' : role.capacity,
                         'org_name' : org.name})
                user_list.append(user_dict)
        return user_list


class ODVLExtension(p.SingletonPlugin):
    p.implements(p.IConfigurer, inherit=True)
    p.implements(p.ITemplateHelpers)
    p.implements(p.IActions)


    def get_actions(self):
        return {
            'members_of_orgs' : members_of_orgs
        }

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