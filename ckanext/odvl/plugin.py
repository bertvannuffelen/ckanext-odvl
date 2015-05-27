import os
import inspect
import ckan.plugins as p
import ckanext.odvl.helpers as helpers
import ckanext.hierarchy as hierarchy
import ckan.logic as logic
import ckan.new_authz as new_authz
import traceback
import ckan.lib.dictization.model_dictize as model_dictize
from ckanext.hierarchy.model import GroupTreeNode
from ckan import model


@logic.side_effect_free
def members_of_orgs(context, data_dict=None):

    try:

        model = context['model']
        currentuser = context['user']

        #logic.check_access('members_of_orgs', context, data_dict)
        sysadmin = new_authz.is_sysadmin(currentuser)

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
    sysadmin = new_authz.is_sysadmin(currentuser)

    orgs = logic.action.get.organization_list(context, data_dict)

    if (not sysadmin):
        orgs = [org for org in orgs if org['package_count'] > 0]

    return orgs

@logic.side_effect_free
def group_tree_filtered(context, data_dict):
    currentuser = context['user']
    sysadmin = new_authz.is_sysadmin(currentuser)

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


class ODVLExtension(p.SingletonPlugin):
    p.implements(p.IConfigurer, inherit=True)
    p.implements(p.ITemplateHelpers)
    p.implements(p.IActions)


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