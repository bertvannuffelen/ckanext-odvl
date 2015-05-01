import sys
import re
from pprint import pprint
import logging
import ckan.model as model

from ckan.lib.cli import CkanCommand
from ckan.lib.helpers import json
log = logging.getLogger(__name__)

class Odvl(CkanCommand):
    '''Performs ODVL related operations.

    Usage:
        odvl creategroups
            Creates the necessary groups
      
    The commands should be run from the ckanext-odvl directory and expect
    a development.ini file to be present. Most of the time you will
    specify the config explicitly though::

        paster odvl creategroups --config=../ckan/development.ini

    '''

    summary = __doc__.split('\n')[0]
    usage = __doc__
    max_args = 2 
    min_args = 0

    def command(self):
        self._load_config()
        print ''

        if len(self.args) == 0:
            self.parser.print_usage()
            sys.exit(1)
        cmd = self.args[0]
        if cmd == 'creategroups':
            self.creategroups()
        else:
            print 'Command %s not recognized' % cmd

    def creategroups(self):
        from ckan.model import Session
        conn = Session.connection()

        errors = []
        for group_name in ['group1', 'group2']:
            group = model.Group(name=unicode(group_name))
            model.Session.add(group)
            model.setup_default_user_roles(group)

        #model.repo.commit_and_remove()

        Session.commit()
        
        if errors:
            msg = 'Errors were found:\n%s' % '\n'.join(errors)
            print msg

        msg = "Done. Extents generated for %i out of %i packages" % (count,len(packages))

        print msg

