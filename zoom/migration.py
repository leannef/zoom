"""
    zoom.migration

    Zoom middleware for handling stack migrations (version updates)

    TODO: at some point we could see looking to import a site.migrations
    module into this namespace (for the /admin/migrations app to see)
"""
import logging

from zoom.database import connect_database
from zoom.models import ActiveMigration
from zoom.site import Site
from zoom.store import EntityStore


def add_users_latest_activity(request, log):
    """Check that the users model supports the latest activity field"""
    log.debug('Checking for users.latest_activity')
    site = Site(request)
    db = connect_database(site.config)
    fieldnames = [field[0] for field in db('select * from users where 1=2').cursor.description]
    print('called')
    if 'latest_activity' not in fieldnames:
        print('patching')
        log.info('users.latest_activity is missing')
        db('alter table users add column `latest_activity` datetime default NULL AFTER `updated`')
        db('alter table users add KEY `latest_activity` (`latest_activity`)')
        log.info('users.latest_activity has been added')


def handler(request, handler, *rest):
    """Handle migrations as necessary"""
    logger = logging.getLogger(__name__)

    request.profiler.add('checking for migrations')

    # migrations can be enabled via the /admin/migrations application
    site = Site(request)
    db = connect_database(site.config)
    migrations = EntityStore(db, ActiveMigration)

    namespace = globals()
    for migration in migrations:
        if migration.callable:
            namespace[migration.callable](request, logger)

    request.profiler.add('migrations finished')
    result = handler(request, *rest)
    return result
