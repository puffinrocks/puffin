from .docker import get_client, get_application_status, run_service
from .security import get_admin
from .applications import ApplicationStatus, get_application, get_application_name
from .. import app
from datetime import datetime


def init():
    pass

def backup(user, application):
    client = get_client()

    if get_application_status(client, user, application) != ApplicationStatus.DELETED:
        raise Exception("Can't backup running application, user: {}, application: {}"
                .format(user.login, application.application_id))

    backup_name = get_timestamp()

    admin = get_admin()
    backup_application = get_application("_backup")

    for volume in application.volumes:
        full_volume = get_full_volume(user, application, volume)
        full_archive = get_full_archive(user, application, volume, backup_name)
        run_service(admin, backup_application, "backup", 
                BACKUP="puffin_backup", VOLUME=full_volume, ARCHIVE=full_archive)

def restore(user, application, backup_name):
    client = get_client()

    if get_application_status(client, user, application) != ApplicationStatus.DELETED:
        raise Exception("Can't restore running application, user: {}, application: {}"
                .format(user.login, application.application_id))

    admin = get_admin()
    backup_application = get_application("_backup")

    for volume in application.volumes:
        full_volume = get_full_volume(user, application, volume)
        full_archive = get_full_archive(user, application, volume, backup_name)
        run_service(admin, backup_application, "restore", 
                BACKUP="puffin_backup", VOLUME=full_volume, ARCHIVE=full_archive)

def list(user, application):
    admin = get_admin()
    backup_application = get_application("_backup")
    application_name = get_application_name(user, application)

    backups = run_service(admin, backup_application, "list", 
            BACKUP="puffin_backup", VOLUME="puffin_backup", ARCHIVE=application_name)

    return sorted(backups.split(), reverse=True)

def delete_old():
    pass


def get_full_volume(user, application, volume):
    application_name = get_application_name(user, application)
    return application_name + "_" + volume

def get_full_archive(user, application, volume, backup_name):
    application_name = get_application_name(user, application)
    return application_name + "/" + backup_name + "/" + volume

def get_timestamp():
    return datetime.today().strftime("%Y-%m-%d_%H:%M:%S")
