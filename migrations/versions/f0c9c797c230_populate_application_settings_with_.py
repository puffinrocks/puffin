"""populate application_settings with started apps

Revision ID: f0c9c797c230
Revises: 31850461ed3
Create Date: 2017-02-16 01:02:02.951573

"""

# revision identifiers, used by Alembic.
revision = 'f0c9c797c230'
down_revision = '31850461ed3'

from alembic import op
import sqlalchemy as sa

from puffin.core import docker, applications

def upgrade():
    running_applications = docker.get_all_running_applications()
    for running_application in running_applications:
        user = running_application[0]
        application = running_application[1]
        applications.set_application_started(user, application, True)

def downgrade():
    pass
