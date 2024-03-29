import logging
import datetime
import operator
import pylons.config as config
import sqlalchemy.exc
import json
import urllib

import ckan
import ckan.model as model
import ckan.plugins as p
import ckan.lib.search as search
import json

NUM_TOP_PUBLISHERS = 6
NUM_MOST_VIEWED_DATASETS = 10

log = logging.getLogger(__file__)

# Deprecated
def filter_vodap_extras(extras):
    return [extra for extra in extras if extra[0] in ('access_rights', 'language', 'issued', 'modified', 'temporal-extent-begin', 'temporal-extent-end', 'spatial', 'theme')]
            #not in ('publisher', 'publisher_name', 'publisher_uri', 'publisher_email', 'publisher_type', 'contact_name', 'contact_uri')

def is_list(value):
    return isinstance(value, list)

def render_link(s):
    if s and '://' in s:
        return '<a href="'+s+'"> '+s+' </a>'
    else:
        return s

def json_parse(json_string):
    try:
        return json.loads(json_string)
    except:
        return json_string

def recent_updates(n):
    '''
    Return a list of the n most recently updated datasets.
    '''
    context = {'model': model,
               'session': model.Session,
               'user': p.toolkit.c.user or p.toolkit.c.author}
    data = {'rows': n,
            'sort': u'metadata_modified desc',
            'facet': u'false'}
    try:
        search_results = p.toolkit.get_action('package_search')(context, data)
    except search.SearchError:
        search_results = {}
    return search_results.get('results', [])


def top_publishers(groups):
    '''
    Updates the 'packages' field in each group dict (up to a maximum
    of NUM_TOP_PUBLISHERS) to show the number of public datasets in the group.
    '''
    publishers = [g for g in groups if g['packages'] > 0]
    publishers.sort(key=operator.itemgetter('packages'), reverse=True)

    return publishers[:NUM_TOP_PUBLISHERS]


def most_viewed_datasets(num_datasets=NUM_MOST_VIEWED_DATASETS):
    try:

        context = {'model': model,
                   'session': model.Session,
                   'user': p.toolkit.c.user or p.toolkit.c.author}
        data = {'rows': num_datasets,
                'sort': u'views_total desc',
                'facet': u'false',
                'fl': ['id', 'name', 'title', 'modified_date', 'tracking']}
        results = p.toolkit.get_action('package_search')(context, data)

        return [r for r in results.get('results', [])
                if r.get('tracking_summary') and r.get('tracking_summary').get('total') > 0]
    except search.SearchError, e:
        log.error('Error searching for most viewed datasets')
        log.error(e)


'''

def translate(terms, lang, fallback_lang):
    translations = logic.get_action('term_translation_show')(
        {'model': model},
        {'terms': terms, 'lang_codes': [lang]}
    )

    term_translations = {}
    for translation in translations:
        term_translations[translation['term']] = \
            translation['term_translation']

    for term in terms:
        if not term in term_translations:
            translation = logic.get_action('term_translation_show')(
                {'model': model},
                {'terms': [term], 'lang_codes': [fallback_lang]}
            )
            if translation:
                term_translations[term] = translation[0]['term_translation']
            else:
                term_translations[term] = term

    return term_translations


def tags_and_translations(context, vocab, lang, lang_fallback):
    try:
        tags = logic.get_action('tag_list')(context, {'vocabulary_id': vocab})
        tag_translations = translate(tags, lang, lang_fallback)
        return sorted([(t, tag_translations[t]) for t in tags],
                      key=operator.itemgetter(1))
    except logic.NotFound:
        return []


def current_url():
    return p.toolkit.request.environ['CKAN_CURRENT_URL'].encode('utf-8')


def current_locale():
    return i18n.get_locales_dict().get(p.toolkit.request.environ['CKAN_LANG'])\
        or fallback_locale()


def fallback_locale():
    return i18n.get_locales_dict().get(config.get('ckan.locale_default', 'en'))


def root_url():
    locale = p.toolkit.request.environ.get('CKAN_LANG')
    default_locale = p.toolkit.request.environ.get('CKAN_LANG_IS_DEFAULT',
                                                   True)

    if default_locale:
        return '/'
    else:
        return '/{0}/'.format(locale)


def format_description(description):

    try:
        formatted = ckan.misc.MarkdownFormat().to_html(description)
        return genshi.HTML(formatted)
    except Exception:
        error_msg = "<span class='inline-warning'>%s</span>" % \
            p.toolkit._("Cannot render package description")
        return genshi.HTML(error_msg)





def current_date():
    return datetime.date.today().strftime('%d/%m/%Y')


def catalog_url():
    return config.get('ckan.catalog_url', 'http://open-data.europa.eu/')


def group_facets_by_field(fields):
    facet_order = {'tags': 0,
                   'res_format': 1}
    facets = {}
    for field, value in fields:
        if field in facets:
            facets[field].append(value)
        else:
            facets[field] = [value]
    return sorted(facets.items(),
                  key=lambda x: facet_order.get(x[0], len(facet_order)))
    return facets


def groups_available(user):
    context = {'model': model, 'session': model.Session, 'user': user}
    userobj = model.User.get(user)

    ckan_lang = str(current_locale())
    ckan_lang_fallback = str(fallback_locale())

    if Authorizer().is_sysadmin(user):
        group_type = config.get('ckan.default.group_type',
                                'organization')
        groups = logic.get_action('group_list')(
            context, {'all_fields': True})
        groups = [group for group in groups
                  if group.get('type') == group_type]
    elif userobj:
        groups = []
        for group in userobj.get_groups():
            group_dict = dictization.table_dictize(group, context)
            group_dict['display_name'] = group.display_name
            groups.append(group_dict)
    else:
        groups = []

    group_translations = translate(
        [group.get('display_name') for group in groups],
        ckan_lang, ckan_lang_fallback)

    def sort_translations(key):
        # Strip accents first and if equivilant do next stage comparison.
        # leaving space and concatenating is to avoid having todo a real
        # 2 level sort.
        display_name = key[1]
        return (unicode_sort.strip_accents(display_name) +
                '   ' +
                display_name).translate(UNICODE_SORT)

    publishers = [
        (group['name'],
         group_translations[group.get('display_name')] or group['name'])
        for group in groups]
    publishers.sort(key=sort_translations)

    return publishers


def ecportal_date_to_iso(date_string):

    if len(date_string) == len('YYYY'):
        format = '%Y'
    elif len(date_string) == len('YYYY-MM'):
        format = '%Y-%m'
    elif len(date_string) == len('YYYY-MM-DD'):
        format = '%Y-%m-%d'
    else:
        return

    return datetime.datetime.strptime(date_string, format).isoformat()


# TODO: (?) support resource objects as well
def resource_display_name(resource_dict):
    name = resource_dict.get('name', None)
    description = resource_dict.get('description', None)
    if description:
        description = description.split('.')[0]
        max_len = 55
        if len(description) > max_len:
            description = description[:max_len] + '...'
        return description
    elif name:
        return name
    else:
        noname_string = 'no name'
        return '[%s] %s' % (noname_string, resource_dict['id'])


_RESOURCE_DROPDOWN = None


def resource_dropdown():
    global _RESOURCE_DROPDOWN
    if not _RESOURCE_DROPDOWN:
        file_location = config.get(
            'ckan.resource_dropdown',
            '/applications/ecodp/users/ecodp/ckan/ecportal/src/ckanext-ecportal/data/resource_dropdown.json'
        )
        with open(file_location) as resource_file:
            #load then dump to check if its valid early
            _RESOURCE_DROPDOWN = json.loads(resource_file.read())

    return json.dumps(_RESOURCE_DROPDOWN)

_RESOURCE_MAPPING = None


def resource_mapping():
    global _RESOURCE_MAPPING
    if not _RESOURCE_MAPPING:
        file_location = config.get(
            'ckan.resource_mapping',
            '/applications/ecodp/users/ecodp/ckan/ecportal/src/ckanext-ecportal/data/resource_mapping.json'
        )
        with open(file_location) as resource_file:
            _RESOURCE_MAPPING = json.loads(resource_file.read())

    return _RESOURCE_MAPPING


def resource_display_format(resource_dict):
    return format_display_name(resource_dict.get('format'))


def format_display_name(format):
    if format in resource_mapping():
        format = resource_mapping()[format][1]
    return format


def dataset_resource_formats(resources):

    return list(set([r['format'] for r in resources if r.get('format')]))




def approved_search_terms():
    try:
        terms = searchcloud.get_approved(model.Session)
        if terms:
            return searchcloud.approved_to_json(terms)
    except sqlalchemy.exc.ProgrammingError:
        log.error('Could not retrieve search cloud results from database. '
                  'Do the tables exist? Rolling back the session.')
        model.Session.rollback()


def search_url_params(group_name=None):
    # Parameter data is passed to the ckan.controllers.feed.custom.
    # As this current adds search parameters that are not in
    # ['q', 'page', 'sort'] and don't beging with '_' to the
    # Solr 'fq' field, we need to remove ext_boolean here.
    params = [(k, v) for k, v in p.toolkit.request.params.items()
              if not k in ['page', 'ext_boolean']]
    if group_name:
        params.append(('groups', group_name))
    return urllib.urlencode(
        [(k, v.encode('utf-8') if isinstance(v, basestring) else str(v))
         for k, v in params])

'''
