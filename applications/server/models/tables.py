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

#########################################################################

## Adding table that should be used to store procedures on the server

# with this new split table definition it makes sense to just use the automatic id in this table as the procedure_id
db.define_table('procedures',
                #Field('procedure_id', 'bigint', required=True),  # key
                Field('user_id', 'string', required=True),
                Field('name', 'string')  # Name of procedure
                )

db.define_table('procedure_revisions',
                Field('procedure_id', 'bigint', required=True),  # key
                Field('procedure_data', 'text', required=True),  # Actual code for procedure - is check IS_LENGTH(65536) ok?
                # Otherwise use string and specifiy larger length
                Field('last_update', 'datetime', default=datetime.datetime.utcnow(), required=True),
                Field('stable_version', 'boolean', required=True) # True for stable False for not stable
                )


# For the user management team?
db.define_table('devices',
                # if we give the device an ID, we can do checks to verify devices belong to which device
                Field('device_id', 'string', required=True),
                Field('user_email'),
                Field('name', 'string', required=True, default='Unknown Device'), # Name of device
                Field('description', 'text', default=''),
                Field('last_sync', 'datetime', required=True,default=datetime.utcnow()), # TODO: move to synch code?
                )

# This is a table that specifies what procedure runs on what device for what user
db.define_table('runs_on',
                Field('user_email', required=True),
                Field('device_id', 'string', required=True),
                Field('proc_id', 'string', required=True)
                )


## TODO: define the tables that need to be synched "down", for settings, and procedures.
