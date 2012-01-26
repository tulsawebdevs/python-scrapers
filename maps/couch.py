from couchdb.mapping import Document, TextField, DateField

class Facility(Document):
    _id = TextField()
    name = TextField()
    location = TextField()
    href = TextField()

class Inspection(Document):
    _id = TextField()
    facility = TextField()
    date = DateField()
    type = TextField()
    priority = TextField()
    purpose = TextField()
    result = TextField()
    actions = TextField()
