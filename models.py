from peewee import (MySQLDatabase, Model, TextField, AutoField)

db = MySQLDatabase('test', user='admin', password='abc123')
def database():
    class data(Model):
        STT = AutoField()
        tieude = TextField()
        mota = TextField()
        noidung = TextField()

        class Meta:
            database = db
            db_table = 'data'

    data.create_table()
    return data