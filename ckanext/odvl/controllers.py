from ckan.plugins import toolkit
from ckan.model.meta import Session
from ckan.common import response
import ckan.lib.base as base
import ckan.model as model
import ckan.logic as logic
import csv
try: from cStringIO import StringIO
except ImportError: from StringIO import StringIO

if toolkit.check_ckan_version(min_version='2.1'):
    BaseController = toolkit.BaseController
else:
    from ckan.lib.base import BaseController

c = base.c

class OdvlController(BaseController):

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



