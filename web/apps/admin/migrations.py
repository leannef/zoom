"""
    admin.migrations

    Zoom System Migrations
"""
from inspect import getmembers, isfunction

from zoom.collect import Collection
from zoom.models import ActiveMigration
from zoom.store import EntityStore
from zoom.fields import Fields, PulldownField, MemoField


def migration_fields():
    """return the fields for an active migration entity"""
    import zoom.migration

    callables = [o[0] for o in getmembers(zoom.migration) if isfunction(o[1])]

    fields = Fields([
        PulldownField('Callable', name='name', options=callables),
        MemoField('Notes'),
    ])

    return fields


def main(route, request):
    migrations = EntityStore(request.site.db, ActiveMigration)
    fields = migration_fields()
    columns = 'link', 'notes', 'created'
    return Collection(
        fields,
        model=ActiveMigration,
        store=migrations,
        item_name='migration',
        url='/admin/migrations',
        columns=columns,
    )(route, request)
