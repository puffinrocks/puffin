import datetime

from puffin import app
from . import docker
from . import security
from . import applications


def init():
    pass

def backup(user, application):
    client = docker.get_client()

    application_status = docker.get_application_status(client, user, application)
    if application_status not in (applications.ApplicationStatus.DELETED, applications.ApplicationStatus.UPDATING):
        raise Exception("Can't backup running application, user: {}, application: {}"
                .format(user.login, application.application_id))

    backup_name = get_timestamp()

    admin = security.get_admin()
    backup_application = applications.get_application("_backup")

    for volume in application.volumes:
        full_volume = get_full_volume(user, application, volume)
        full_archive = get_full_archive(user, application, volume, backup_name)
        output = docker.run_service(admin, backup_application, "backup", 
                BACKUP="puffin_backup", VOLUME=full_volume, ARCHIVE=full_archive)
        if output:
            print(output)

def restore(user, application, backup_name):
    client = docker.get_client()

    if docker.get_application_status(client, user, application) != applications.ApplicationStatus.DELETED:
        raise Exception("Can't restore running application, user: {}, application: {}"
                .format(user.login, application.application_id))

    admin = security.get_admin()
    backup_application = applications.get_application("_backup")

    for volume in application.volumes:
        full_volume = get_full_volume(user, application, volume)
        full_archive = get_full_archive(user, application, volume, backup_name)
        output = docker.run_service(admin, backup_application, "restore", 
                BACKUP="puffin_backup", VOLUME=full_volume, ARCHIVE=full_archive)
        if output:
            print(output)

def list(user, application):
    admin = security.get_admin()
    backup_application = applications.get_application("_backup")
    application_name = applications.get_application_name(user, application)

    backups = docker.run_service(admin, backup_application, "list", 
            BACKUP="puffin_backup", VOLUME="puffin_backup", ARCHIVE=application_name)

    return sorted(backups.split(), reverse=True)

def delete_old():
    pass


def get_full_volume(user, application, volume):
    application_name = applications.get_application_name(user, application)
    return application_name + "_" + volume

def get_full_archive(user, application, volume, backup_name):
    application_name = applications.get_application_name(user, application)
    return application_name + "/" + backup_name + "/" + volume

def get_timestamp():
    return datetime.datetime.today().strftime("%Y-%m-%d_%H:%M:%S")
