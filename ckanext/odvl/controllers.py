from ckan.plugins import toolkit
from ckan.model.meta import Session
from ckan.common import response
import ckan.lib.base as base
import ckan.model as model
import ckan.logic as logic
import unicodecsv as csv
try: from cStringIO import StringIO
except ImportError: from StringIO import StringIO

if toolkit.check_ckan_version(min_version='2.1'):
    BaseController = toolkit.BaseController
else:
    from ckan.lib.base import BaseController

c = base.c

class OdvlController(BaseController):

    def summary_facet(self, facet, format):

        context = {'model': model,
                   'user': c.user, 'auth_user_obj': c.userobj}

        logic.check_access('sysadmin', context, {})

        #import ckan.model as model
        #engine = model.meta.engine
        conn = Session.connection()

        facet_title = None
        sql = None

        if facet == 'org':
            facet_title = 'Organization'
            sql = '''
                SELECT grp.name,
                       COUNT(CASE WHEN p.state = 'active' THEN 1 END) as TotalActive,
                       COUNT(CASE WHEN p.private = TRUE AND p.state = 'active' THEN 1 END) as PrivateActive,
                       COUNT(CASE WHEN p.state = 'draft' THEN 1 END) as Draft,
                       COUNT(CASE WHEN p.state = 'deleted' THEN 1 END) as Deleted
                   FROM package AS p
                   LEFT OUTER JOIN public.group AS grp ON grp.id = p.owner_org
                   GROUP BY grp.name
                   ORDER BY TotalActive DESC
            '''
        elif facet == 'user':
            facet_title = 'User'
            sql = '''
                SELECT u.name,
                       COUNT(CASE WHEN p.state = 'active' THEN 1 END) as TotalActive,
                       COUNT(CASE WHEN p.private = TRUE AND p.state = 'active' THEN 1 END) as PrivateActive,
                       COUNT(CASE WHEN p.state = 'draft' THEN 1 END) as Draft,
                       COUNT(CASE WHEN p.state = 'deleted' THEN 1 END) as Deleted
                   FROM package AS p
                   LEFT OUTER JOIN public.user AS u ON u.id = p.creator_user_id
                   GROUP BY u.name
                   ORDER BY TotalActive DESC
            '''
        elif facet == 'theme':
            facet_title = 'Theme'
            sql = '''
                SELECT e.value,
                       COUNT(CASE WHEN p.state = 'active' THEN 1 END) as TotalActive,
                       COUNT(CASE WHEN p.private = TRUE AND p.state = 'active' THEN 1 END) as PrivateActive,
                       COUNT(CASE WHEN p.state = 'draft' THEN 1 END) as Draft,
                       COUNT(CASE WHEN p.state = 'deleted' THEN 1 END) as Deleted
                   FROM package AS p
                   INNER JOIN public.package_extra AS e ON e.package_id = p.id
                   WHERE e.key = 'theme'
                   GROUP BY e.value
                   ORDER BY TotalActive DESC
            '''
        elif facet == 'publisher':
            facet_title = 'Publisher'
            sql = '''
                SELECT e.value,
                       COUNT(CASE WHEN p.state = 'active' THEN 1 END) as TotalActive,
                       COUNT(CASE WHEN p.private = TRUE AND p.state = 'active' THEN 1 END) as PrivateActive,
                       COUNT(CASE WHEN p.state = 'draft' THEN 1 END) as Draft,
                       COUNT(CASE WHEN p.state = 'deleted' THEN 1 END) as Deleted
                   FROM package AS p
                   INNER JOIN public.package_extra AS e ON e.package_id = p.id
                   WHERE e.key = 'publisher_name'
                   GROUP BY e.value
                   ORDER BY TotalActive DESC
            '''
        elif facet == 'tag':
            facet_title = 'Tag'
            sql = '''
             SELECT t.name,
                       COUNT(CASE WHEN p.state = 'active' THEN 1 END) as TotalActive,
                       COUNT(CASE WHEN p.private = TRUE AND p.state = 'active' THEN 1 END) as PrivateActive,
                       COUNT(CASE WHEN p.state = 'draft' THEN 1 END) as Draft,
                       COUNT(CASE WHEN p.state = 'deleted' THEN 1 END) as Deleted
                   FROM package AS p
                   INNER JOIN package_tag AS pt ON pt.package_id = p.id
                   INNER JOIN tag AS t ON pt.tag_id = t.id
                   WHERE pt.state = 'active'
                   GROUP BY t.name
                   ORDER BY TotalActive DESC
            '''
        elif facet == 'extra':
            facet_title = 'Extra'
            sql = '''
                SELECT e.key,
                       COUNT(CASE WHEN p.state = 'active' THEN 1 END) as TotalActive,
                       COUNT(CASE WHEN p.private = TRUE AND p.state = 'active' THEN 1 END) as PrivateActive,
                       COUNT(CASE WHEN p.state = 'draft' THEN 1 END) as Draft,
                       COUNT(CASE WHEN p.state = 'deleted' THEN 1 END) as Deleted
                   FROM package AS p
                   INNER JOIN public.package_extra AS e ON e.package_id = p.id
                   GROUP BY e.key
                   ORDER BY TotalActive DESC
            '''
        elif facet == 'license':
            facet_title = 'License'
            sql = '''
                SELECT p.license_id,
                       COUNT(CASE WHEN p.state = 'active' THEN 1 END) as TotalActive,
                       COUNT(CASE WHEN p.private = TRUE AND p.state = 'active' THEN 1 END) as PrivateActive,
                       COUNT(CASE WHEN p.state = 'draft' THEN 1 END) as Draft,
                       COUNT(CASE WHEN p.state = 'deleted' THEN 1 END) as Deleted
                   FROM package AS p
                   GROUP BY p.license_id
                   ORDER BY TotalActive DESC
            '''

        csvout = StringIO()
        csvwriter = csv.writer(
            csvout,
            quoting=csv.QUOTE_NONNUMERIC,
        )

        csvwriter.writerow([facet_title, 'Total Active', 'Private Active', 'Draft', 'Deleted'])

        for t in conn.execute(sql).fetchall():
            csvwriter.writerow(t)

        csvout.seek(0)

        response.headers['Content-Type'] = 'text/csv'

        return csvout.read()

    def summary_csv(self):

        context = {'model': model,
                   'user': c.user, 'auth_user_obj': c.userobj}

        logic.check_access('sysadmin', context, {})

        #import ckan.model as model
        #engine = model.meta.engine
        conn = Session.connection()

        sql = '''
            SELECT DISTINCT p.id,
                   p.name,
                   u.name,
                   grp.name,
                   p.metadata_modified,
                   p.private,
                   hs.title,
                   ( SELECT bool_or(ho.current) FROM harvest_object AS ho WHERE ho.package_id = p.id GROUP BY ho.package_id) AS isCurrent,
                   p.state
               FROM package AS p
               LEFT OUTER JOIN public.user AS u ON u.id = p.creator_user_id
               LEFT OUTER JOIN public.group AS grp ON grp.id = p.owner_org
               LEFT OUTER JOIN harvest_object AS ho ON ho.package_id = p.id
               LEFT OUTER JOIN harvest_source AS hs ON ho.harvest_source_id = hs.id
               ORDER BY grp.name, p.metadata_modified
        '''

        csvout = StringIO()
        csvwriter = csv.writer(
            csvout,
            quoting=csv.QUOTE_NONNUMERIC
        )

        csvwriter.writerow(['ID', 'name', 'creator', 'org', 'modification date', 'private?', 'harvestSource', 'current', 'state'])

        for t in conn.execute(sql).fetchall():
            csvwriter.writerow(t)

        csvout.seek(0)

        response.headers['Content-Type'] = 'text/csv'

        return csvout.read()



