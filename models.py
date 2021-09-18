from peewee import (MySQLDatabase, Model, TextField, AutoField, CharField)

db = MySQLDatabase('test', user='admin', password='abc123')

class BaseModel(Model):
    class Meta:
        database = db

class data(BaseModel):
    STT = AutoField()
    tieude = CharField()
    mota = TextField()
    noidung = TextField()
    https = CharField()

def database():
    data.create_table()
    return data
