import os
import re
from ckan.plugins.toolkit import Invalid
import inspect
import ckan.plugins as p
import ckanext.odvl.helpers as helpers
import ckanext.hierarchy as hierarchy
import ckan.logic as logic
import ckan.authz as authz
import traceback
import ckan.lib.dictization.model_dictize as model_dictize
from ckanext.hierarchy.model import GroupTreeNode
from ckanext.spatial.interfaces import ISpatialHarvester
import ckan.plugins.toolkit as toolkit
import ckan.lib.navl.dictization_functions as df
from ckan import model


EMAIL_REGEX = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")

@logic.side_effect_free
def members_of_orgs(context, data_dict=None):

    try:

        model = context['model']
        currentuser = context['user']

        #logic.check_access('members_of_orgs', context, data_dict)
        sysadmin = authz.is_sysadmin(currentuser)

        if sysadmin:
            users = model.Session.query(model.User) \
                .filter(model.User.state == 'active')

            user_list = []

            for user in users.all():
                if (user):
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
                            if org:
                                user_dict['orgs'].append(
                                    {'role' : role.capacity,
                                     'org_name' : org.name})
                        if len(user_dict['orgs'])>0:
                            user_list.append(user_dict)
            return user_list
    except:
        print traceback.format_exc()

@logic.side_effect_free
def organization_list(context, data_dict):

    currentuser = context['user']
    sysadmin = authz.is_sysadmin(currentuser)

    orgs = logic.action.get.organization_list(context, data_dict)

    if (not sysadmin):
        orgs = [org for org in orgs if org['package_count'] > 0]

    return orgs

@logic.side_effect_free
def group_tree_filtered(context, data_dict):
    currentuser = context['user']
    sysadmin = authz.is_sysadmin(currentuser)

    model = context['model']
    group_type = data_dict.get('type', 'group')

    group_counts = model_dictize.get_group_dataset_counts()['owner_org']

    filtered_groups = []
    for group in model.Group.get_top_level_groups(type=group_type):
        branch = _group_tree_branch(group, type=group_type, group_counts=None if sysadmin else group_counts)
        if len(branch['children']) > 0 or branch['id'] in group_counts or sysadmin:
            filtered_groups.append(branch)

    return filtered_groups

def _group_tree_branch(root_group, highlight_group_name=None, type='group', group_counts=None):
    '''Returns a branch of the group tree hierarchy, rooted in the given group.

    :param root_group_id: group object at the top of the part of the tree
    :param highlight_group_name: group name that is to be flagged 'highlighted'
    :returns: the top GroupTreeNode of the tree
    '''
    nodes = {}  # group_id: GroupTreeNode()
    root_node = nodes[root_group.id] = GroupTreeNode(
        {'id': root_group.id,
         'name': root_group.name,
         'title': root_group.title})
    if root_group.name == highlight_group_name:
        nodes[root_group.id].highlight()
        highlight_group_name = None
    for group_id, group_name, group_title, parent_id in \
            root_group.get_children_group_hierarchy(type=type):
        node = GroupTreeNode({'id': group_id,
                              'name': group_name,
                              'title': group_title})
        if not group_counts or group_id in group_counts:
            nodes[parent_id].add_child_node(node)
            if highlight_group_name and group_name == highlight_group_name:
                node.highlight()
            nodes[group_id] = node
    return root_node

def is_valid_license(value):
    if value is df.missing:
        return 'notspecified'

    licenses = model.Package.get_license_register().licenses
    for lic in licenses:
        if lic['id'] == value:
            return value

    # TODO uncomment this to enforce predefined licenses
    #if value and not value is df.missing:
    #    raise Invalid("License is unknown: " + value)

    if value is df.missing:
        value = None

    return value

def clean_email(value):
    if (value and value.startswith("mailto:")):
        value = value[7:].strip()

    if value is df.missing:
            value = None

    return value

def is_email(value):
    if not EMAIL_REGEX.match(value):
        raise Invalid("Value is not an email: " + value)
    return value

def validate_extra(extra_name, validator_list):
    def validator(key, data, errors, context):
        extra_key = (key[0], key[1], 'key')
        if data.get(extra_key) == extra_name:
            for extra_validator in validator_list:
                data[key] = extra_validator(data[key])

    return validator

class ODVLExtension(p.SingletonPlugin, p.toolkit.DefaultDatasetForm):
    p.implements(p.IConfigurer, inherit=True)
    p.implements(p.ITemplateHelpers)
    p.implements(p.IActions)
    p.implements(p.IDatasetForm)
    p.implements(p.IRoutes, inherit=True)

    def after_map(self, map):

        controller = 'ckanext.odvl.controllers:OdvlController'
        map.connect('/summary.csv', controller=controller, action='summary_csv')

        return map

    def is_fallback(self):
        # Return True to register this plugin as the default handler for
        # package types not handled by any other IDatasetForm plugin.
        return True

    def package_types(self):
        # This plugin doesn't handle any special package types, it just
        # registers itself as the default (above).
        return []

    def _modify_package_schema(self, schema, isHarvesting=False):
        schema.update({
            'license_id': [is_valid_license],
            'license_title': [],
            'maintainer_email': [clean_email]
        })
        schema['extras']['value'].append(validate_extra('contact_email', [clean_email]))

        schema['resources'].update({
            'url' : [ p.toolkit.get_validator('not_empty') ]
        })

        if not isHarvesting:
            schema.update({
                'title': [p.toolkit.get_validator('not_empty')],
                #'notes': [p.toolkit.get_validator('not_empty')],
                'owner_org': [p.toolkit.get_validator('not_empty')],
                'notes': [p.toolkit.get_validator('not_empty')],
                'maintainer_email': [p.toolkit.get_validator('not_empty'), clean_email, is_email]
            })

            schema['resources'].update({
                'description' : [ p.toolkit.get_validator('not_empty') ],
                'name' : [ p.toolkit.get_validator('not_empty') ]
            })

        return schema

    def create_package_schema(self, isHarvesting=True):
        schema = super(ODVLExtension, self).create_package_schema()
        schema = self._modify_package_schema(schema, isHarvesting=isHarvesting)
        return schema

    def update_package_schema(self, isHarvesting=True):
        schema = super(ODVLExtension, self).update_package_schema()
        schema = self._modify_package_schema(schema, isHarvesting=isHarvesting)
        return schema

    def get_actions(self):
        return {
            'members_of_orgs' : members_of_orgs,
            'organization_list' : organization_list,
            'group_tree_filtered': group_tree_filtered
        }

    def update_config(self, config):

        #config['ckan.site_logo'] = '/images/logo04.gif'
        #config['ckan.site_intro_text'] = 'test intro'
        # Defining and hiding the spatial extra field
        if ('ckan.extra_resource_fields' in config):
            if ('spatial' not in config['ckan.extra_resource_fields']):
                config['ckan.extra_resource_fields'] += ' spatial'
        else:
            config['ckan.extra_resource_fields'] = 'spatial'

        config['package_hide_extras'] = 'spatial guid uri'
        #config['search.facets'] = 'groups tags res_format license_id'
        config['ckan.locale_default'] = 'nl'
        config['ckan.locale_order'] = config['ckan.locales_offered'] = 'nl fr de en'
        config['ckan.site_title'] = 'Vlaanderen.be'
        config['ckan.template_title_deliminater'] = '|'
        config['ckan.favicon'] = 'http://d201gzvprbtpxy.cloudfront.net/sites/all/themes/portal_q4_2013/favicon.ico'
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

    def validate(self, context, data_dict, schema, action):
        # when triggered through harvesters, default schema is taken (see usage of default_create_package_schema in harvesters)
        # override this method to enforce our schema

        if (action == 'package_create'):
            schema = self.create_package_schema(isHarvesting = (not context.get('save')))
        elif (action == 'package_update'):
            schema = self.update_package_schema(isHarvesting = (not context.get('save')))

        return toolkit.navl_validate(data_dict, schema, context)

    def get_helpers(self):
        return {
                'recent_updates': helpers.recent_updates,
                'top_publishers': helpers.top_publishers,
                'most_viewed_datasets': helpers.most_viewed_datasets,
                }

class GeopuntHarvester(p.SingletonPlugin):
    p.implements(ISpatialHarvester, inherit=True)

    def get_package_dict(self, context, data_dict):
        package_dict = data_dict['package_dict']
        opendataTag = next((x for x in package_dict['tags'] if x['name'].lower() == 'vlaamse open data'), None)
        kosteloosTag = next((x for x in package_dict['tags'] if x['name'].lower() == 'kosteloos'), None)

        if (opendataTag):
            if (kosteloosTag):
                package_dict['license_id'] = 'gratis-hergebruik-1.0'
            else:
                package_dict['license_id'] = 'Gratis Vlaamse Open Data'
        #else:   #this should not happen - only 'Vlaamse Open Data' datasets should be harvested

        return package_dict