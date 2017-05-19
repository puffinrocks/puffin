import sqlalchemy
import sqlalchemy.orm
import sqlalchemy.orm.attributes
import sqlalchemy.dialects.postgresql
import flask_sqlalchemy
import flask_migrate

from puffin import app


db = flask_sqlalchemy.SQLAlchemy()


def init():
    url = get_url(app.config["DB_USER"], app.config["DB_PASSWORD"],
        app.config["DB_HOST"], app.config["DB_PORT"], app.config["DB_NAME"])
    app.config['SQLALCHEMY_DATABASE_URI'] = url

    # Track modifications of objects and emit signals, expensive, perhaps disable
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

    db.init_app(app)
    # See http://piotr.banaszkiewicz.org/blog/2012/06/29/flask-sqlalchemy-init_app/, option 2
    db.app = app

    migrate = flask_migrate.Migrate(app, db)

def create(name):
    "Create database if it does not exist"
    url = get_url(app.config["DB_USER"], app.config["DB_PASSWORD"],
        app.config["DB_HOST"], app.config["DB_PORT"], "postgres")

    engine = sqlalchemy.create_engine(url)
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
    mapper = sqlalchemy.orm.object_mapper(model)
    for column in mapper.columns.values():
        if isinstance(column.type, sqlalchemy.dialects.postgresql.JSON):
            sqlalchemy.orm.attributes.flag_modified(model, column.name)

    db.session.add(model)

