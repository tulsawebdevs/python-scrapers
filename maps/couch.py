from couchdb.mapping import Document, TextField, DateField, FloatField

class Facility(Document):
    _id = TextField()
    name = TextField()
    location = TextField()
    latitude = FloatField()
    longitude = FloatField()
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
