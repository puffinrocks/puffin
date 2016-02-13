import uuid
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import mapper, object_mapper
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.dialects.postgresql import UUID, JSON
from flask.ext.migrate import Migrate

from .. import app
from .model import User, ApplicationSettings


db = SQLAlchemy()


user_table = db.Table('user',
    db.Column('user_id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    db.Column('login', db.String(32), nullable=False),
    db.Column('name', db.String(128), nullable=False),
    db.Column('email', db.String(256), nullable=False),
    db.Column('password', db.String(256), nullable=True),
    db.Column('active', db.Boolean()),
    db.Column('confirmed_at', db.DateTime()),
)

db.Index('idx_user_login', user_table.c.login, unique=True)
db.Index('idx_user_email', user_table.c.email, unique=True)

mapper(User, user_table)


application_settings_table = db.Table('application_settings',
    db.Column('application_settings_id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    db.Column('user_id', UUID(as_uuid=True), nullable=False),
    db.Column('application_id', db.String(64), nullable=False),
    db.Column('settings', JSON, nullable=False),
)

db.Index('idx_application_settings', application_settings_table.c.user_id,
    application_settings_table.c.application_id, unique=True)

mapper(ApplicationSettings, application_settings_table)


def init():
    url = get_url(app.config["DB_USER"], app.config["DB_PASSWORD"], 
        app.config["DB_HOST"], app.config["DB_PORT"], app.config["DB_NAME"])
    app.config['SQLALCHEMY_DATABASE_URI'] = url
    
    db.init_app(app)
    # See http://piotr.banaszkiewicz.org/blog/2012/06/29/flask-sqlalchemy-init_app/, option 2
    db.app = app

    migrate = Migrate(app, db)

def create(name):
    "Create database if it does not exist"
    url = get_url(app.config["DB_USER"], app.config["DB_PASSWORD"], 
        app.config["DB_HOST"], app.config["DB_PORT"], "postgres")
 
    engine = create_engine(url)
    with engine.connect() as conn:
 
        result = conn.execute(
            "SELECT 1 FROM pg_catalog.pg_database WHERE datname='{}'"
            .format(name))
        if result.first():
            return False
        
        conn.execute("COMMIT")
        conn.execute("CREATE DATABASE {}".format(name))

    return True

def get_url(user, password, host, port, name):
    string = "postgresql://"
    
    if user: 
        string += user
        if password:
            string += ":" + password
        string += "@"

    if host:
        string += host

    if port:
        string += ":" + port

    if name:
        string += "/" + name

    return string


def update_model_with_json(model):
    # Needed for JSON fields, see https://bashelton.com/2014/03/updating-postgresql-json-fields-via-sqlalchemy/
    mapper = object_mapper(model)
    for column in mapper.columns.values():
        if isinstance(column.type, JSON):
            flag_modified(model, column.name)
    
    db.session.add(model)
    db.session.commit()

