import uuid

import sqlalchemy.orm
from sqlalchemy.dialects import postgresql

from .db import db
from . import applications
from . import security


user_table = db.Table('user',
    db.Column('user_id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    db.Column('login', db.String(32), nullable=False),
    db.Column('name', db.String(128), nullable=False),
    db.Column('email', db.String(256), nullable=False),
    db.Column('password', db.String(256), nullable=True),
    db.Column('active', db.Boolean()),
    db.Column('confirmed_at', db.DateTime()),
)

db.Index('idx_user_login', user_table.c.login, unique=True)
db.Index('idx_user_email', user_table.c.email, unique=True)

sqlalchemy.orm.mapper(security.User, user_table)


application_settings_table = db.Table('application_settings',
    db.Column('application_settings_id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    db.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
    db.Column('application_id', db.String(64), nullable=False),
    db.Column('settings', postgresql.JSON, nullable=False),
)

db.Index('idx_application_settings', application_settings_table.c.user_id,
    application_settings_table.c.application_id, unique=True)

sqlalchemy.orm.mapper(applications.ApplicationSettings, application_settings_table)


def init():
    pass
