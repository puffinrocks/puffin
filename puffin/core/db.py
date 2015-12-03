import uuid
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import mapper
from sqlalchemy.dialects.postgresql import UUID
from flask.ext.migrate import Migrate

from .. import app
from .model import User, AppInstallation


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


app_installation_table = db.Table('app_installation', 
    db.Column('app_installation_id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    db.Column("version_id", db.Integer(), nullable=False),
    db.Column('user_id', UUID(as_uuid=True), db.ForeignKey(user_table.c.user_id), nullable=False),
    db.Column('app_id', db.String(128)),
    db.Column('status', db.Integer(), nullable=False),
)

db.Index('idx_app_installation_user_id_app_id', 
    app_installation_table.c.user_id, app_installation_table.c.app_id, unique=True)

mapper(AppInstallation, app_installation_table, 
    version_id_col=app_installation_table.c.version_id, 
    properties={
        'user': db.relationship(User, lazy="joined"),
    })


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


