from .docker import get_client, get_application_status, run_service
from .security import get_user, get_admin
from .applications import ApplicationStatus, get_application, get_application_name
from .. import app
from datetime import datetime


def init():
    pass

def backup(user_login, application_id):
    user = get_user(user_login)
    if not user:
        raise Exception("User {} does not exist".format(user_login))

    application = get_application(application_id)
    if not application:
        raise Exception("Application {} does not exist".format(application_id))

    client = get_client()

    if get_application_status(client, user, application) != ApplicationStatus.DELETED:
        raise Exception("Can't backup application that is not stopped, user: {}, application: {}"
                .format(user.login, application.application_id))

    application_name = get_application_name(user, application)

    timestamp = datetime.today().strftime("%Y-%m-%d_%H:%M:%S")

    admin = get_admin()
    backup_application = get_application("_backup")

    for volume in application.volumes:
        full_volume = application_name + "_" + volume
        full_archive = application_name + "/" + timestamp + "/" + volume
        run_service(client, admin, backup_application, "backup", 
                BACKUP="puffin_backup", VOLUME=full_volume, ARCHIVE=full_archive)

def restore():
    pass

def delete_old():
    pass

def create_volumes():
    pass
