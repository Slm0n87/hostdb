from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
domain = Table('domain', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('name', String(length=64)),
)

host = Table('host', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('hostname', String(length=64)),
    Column('domain_id', Integer),
    Column('role_id', Integer),
    Column('stage_id', Integer),
)

role = Table('role', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('name', String(length=64)),
)

stage = Table('stage', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('name', String(length=64)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['domain'].create()
    post_meta.tables['host'].create()
    post_meta.tables['role'].create()
    post_meta.tables['stage'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['domain'].drop()
    post_meta.tables['host'].drop()
    post_meta.tables['role'].drop()
    post_meta.tables['stage'].drop()
