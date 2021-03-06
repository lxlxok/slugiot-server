import datetime

from gluon import current
import access
import logging
import re

logger = logging.getLogger("web2py.app.server")
logger.setLevel(logging.INFO)

auth = current.auth

####### Helper Functions ##########

def _check_name_and_perms_(user_email, device_id, procedure_name):
    db = current.db
    proc_table = db.procedures

    # check that user has permissions to add a procedure to the device
    if not access.can_create_procedure(device_id, user_email):
        logger.error("User " + str(user_email) +
                    " does not have permission to create a procedure on device: " + str(device_id))
        return False

    # device should not have two procedures of the same name
    query = db((proc_table.device_id == device_id) &
               (proc_table.name == procedure_name))
    if not query.isempty():
        logger.error("Device " + str(device_id) + " already contains a procedure of name " + str(procedure_name))
        return False

    # name should not break file system
    result = re.search("[^a-zA-Z0-9._-]", str(procedure_name))
    if result:
        logger.error("Procedure name \"" + str(procedure_name) + "\" is not allowed. Use only numbers, letters, _, -, and .")
        return False

    return True

def _get_most_recent_date_(procedure_id, is_stable):
    db = current.db
    revisions_table = db.procedure_revisions

    # Get the most recent date, either stable or absolute
    max = revisions_table.last_update.max()
    if is_stable:
        date = db((revisions_table.procedure_id == procedure_id) &
                  (revisions_table.is_stable == is_stable)).select(max).first()[max]
    else:
        date = db(revisions_table.procedure_id == procedure_id).select(max).first()[max]

    return date

####### API FOR EDITOR TEAM ##########

def create_procedure(procedure_name, device_id):
    """
    This function should be called when a new procedure is created in the editor.

    :param procedure_name: Name of the new procedure
    :type procedure_name: str
    :param device_id: Device ID associated with device on which user wants to create proc
    :type device_id: str
    :return: ID associated with new procedure (procedure_id in revisions table)
    :rtype: long
    """
    db = current.db
    auth = current.auth
    proc_table = db.procedures

    user_email = auth.user.email

    if not _check_name_and_perms_(user_email, device_id, procedure_name):
        return None

    pid = proc_table.insert(device_id = device_id, name = procedure_name)
    access.add_permission(device_id = device_id, user_email = user_email, procedure_id = pid)

    return pid

def delete_procedure(procedure_id, device_id):
    """
    This function should be called when a procedure should be deleted

    :param procedure_name: Name of the new procedure
    :type procedure_name: str
    :param device_id: Device ID associated with device on which user wants to create proc
    :type device_id: str
    :return:
    :rtype:
    """
    db = current.db
    auth = current.auth
    proc_table = db.procedures
    revisions_table = db.procedure_revisions

    user_email = auth.user.email

    if access.can_delete_procedure(device_id, user_email, procedure_id):
        db(proc_table.id == procedure_id).delete()
        db(revisions_table.procedure_id == procedure_id).delete()

def change_procedure_name(procedure_id, new_procedure_name):
    """
    This function should be called when a procedure name change is desired

    :param procedure_id: Procedure ID for which code should be fetched
    :type procedure_id: long
    :param procedure_name: New name for the procedure
    :type procedure_name: str
    :return:
    :rtype:
    """

    db = current.db
    auth = current.auth
    proc_table = db.procedures

    user_email = auth.user.email
    device_id = db(proc_table.id == procedure_id).select().first().device_id

    if not _check_name_and_perms_(user_email, device_id, new_procedure_name):
        return

    record = db(proc_table.id == procedure_id).select().first()
    record.update_record(name = new_procedure_name)

def get_procedures_for_edit(device_id):
    """
    This function returns all procedure IDs that are associated with a given user to edit

    :param device_id: Device ID associated with device on which user wants to create proc
    :type device_id: str
    :return: List of procedure IDs associated with device
    :rtype:
    """
    db = current.db
    auth = current.auth
    proc_table = db.procedures

    user_email = auth.user.email

    # Get all relevant records for device_id
    records = db(proc_table.device_id == device_id).select()

    # Create list of procedure IDs from records
    procedure_ids = []
    for row in records:
        if access.can_edit_procedure(user_email, device_id, row.id):
            procedure_ids.append(row.id)

    return procedure_ids

def get_procedures_name_for_edit(device_id):
    """
    This function returns all procedure names that are associated with a given user to edit

    :param device_id: Device ID associated with device on which user wants to create proc
    :type device_id: str
    :return: List of procedure names associated with device
    :rtype:
    """
    db = current.db
    auth = current.auth
    proc_table = db.procedures

    user_email = auth.user.email

    # Get all relevant records for device_id
    records = db(proc_table.device_id == device_id).select()

    # Create list of procedure names from records
    procedure_names = []
    for row in records:
        if access.can_edit_procedure(user_email, device_id, row.id):
            procedure_names.append(row.name)

    return procedure_names

def get_procedures_for_view(device_id):
    """
    This function returns all procedure IDs that are associated with a given user to view ONLY

    :param device_id: Device ID associated with device on which user wants to create proc
    :type device_id: str
    :return: List of procedure IDs associated with device
    :rtype:
    """

    db = current.db
    auth = current.auth
    proc_table = db.procedures

    # Get all relevant records for user_email
    user_email = auth.user.email

    records = db(proc_table.device_id == device_id).select()

    # Create list of procedure IDs from records
    procedure_ids = []
    for row in records:
        if ((not access.can_edit_procedure(user_email, device_id, row.id)) and
            access.can_view_procedure(user_email, device_id, row.id)):
            procedure_ids.append(row.id)

    return procedure_ids

def get_procedure_data(procedure_id, is_stable):
    """
    Returns actual code that corresponds to a given procedure ID.
    Returns either the most recent stable version or the most recent absolute version.

    :param procedure_id: Procedure ID for which code should be fetched
    :type procedure_id: long
    :param stable: Flag that determines whether the code returned should be most recent stable or just the most recent
    :type stable: bool
    :return: Data stored for the procedure
    :rtype: str
    """

    db = current.db
    revisions_table = db.procedure_revisions

    date = _get_most_recent_date_(procedure_id, is_stable)

    # Return the data corresponding the procedure ID and determined date
    return db((revisions_table.procedure_id == procedure_id) & (revisions_table.last_update == date)).select(revisions_table.procedure_data).first().procedure_data

def get_procedure_name(procedure_id):
    """
    Returns actual code that corresponds to a given procedure ID.
    Returns either the most recent stable version or the most recent absolute version.

    :param procedure_id: Procedure ID for which code should be fetched
    :type procedure_id: long
    :param stable: Flag that determines whether the code returned should be most recent stable or just the most recent
    :type stable: bool
    :return: Data stored for the procedure
    :rtype: str
    """

    db = current.db
    proc_table = db.procedures

    # Return the data corresponding the procedure ID and determined date
    return db(proc_table.id == procedure_id).select(proc_table.name).first().name

def save(procedure_id, procedure_data, is_stable):
    """
    Save code corresponding to a procedure ID as either a stable version or a temporary version

    :param procedure_id: Procedure ID for which code should be fetched
    :type procedure_id: long
    :param procedure_data: Code that should be saved
    :type procedure_data: str
    :param stable: Flag that determines whether the code should be sent to client on next request or not
    :type stable: bool
    """

    db = current.db
    revisions_table = db.procedure_revisions

    # Insert new record to revisions table
    revisions_table.insert(procedure_id = procedure_id,
                           procedure_data = procedure_data,
                           last_update = datetime.datetime.utcnow(),
                           is_stable = is_stable)

    # Only keep temporary revisions until next stable revision comes in
    # Clean up old temporary revisions upon stable save
    if is_stable:
        db((revisions_table.procedure_id == procedure_id) &
           (revisions_table.is_stable == False)).delete()