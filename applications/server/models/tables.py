#########################################################################
## Define your tables below, for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)

from datetime import datetime

# For the user management team?
db.define_table('devices',
                # if we give the device an ID, we can do checks to verify devices belong to which device
                Field('device_id', 'string', required=True),
                # we can always an ID for something
                Field('user_id', db.auth_user, default=auth.user_id),
                # user should give rbp a name
                Field('name', 'string', required=True, default='Unknown Device'),
                # perhaps a description as well?
                Field('description', 'text', default=''),
                # part of what the UI calls for
                Field('last_sync', 'datetime', required=True,default=datetime.utcnow()),
                # status of the device
                Field('status', 'integer', required=True, default=3)
                )

# This is a table that specifies what procedure runs on what device for what user
db.define_table('runs_on',
                Field('user_id', db.auth_user, required=True, default=auth.user_id),
                Field('device_id', 'string', required=True),
                Field('proc_id', 'string', required=True)
                )

## These correspond to client tables.

db.define_table('logs',
                Field('device_id'),
                Field('time_stamp', 'datetime', default=datetime.utcnow()),
                Field('modulename'),
                Field('log_level', 'integer'), #  int, 0 = most important.
                Field('log_message', 'text'),
                )

db.define_table('outputs',
                Field('device_id'),
                Field('time_stamp', 'datetime', default=datetime.utcnow()),
                Field('modulename'),
                Field('name'), # Name of variable
                Field('output_value', 'text'), # Json, short please
                Field('tag')
                )

db.define_table('module_values',
                Field('device_id'),
                Field('time_stamp', 'datetime', default=datetime.utcnow()),
                Field('modulename'),
                Field('name'),  # Name of variable
                Field('output_value', 'text'),  # Json, short please
                )