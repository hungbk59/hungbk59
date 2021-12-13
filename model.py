import mysql.connector

from peewee import MySQLDatabase, Model, TextField, AutoField, CharField


cretedb = mysql.connector.connect(
    host="localhost",
    user="admin",
    password="abc123")
mycur = cretedb.cursor()
try:
    mycur.execute("CREATE DATABASE test")
except:
    print('Database exists')
    
db = MySQLDatabase('test', user='admin', password='abc123')


class BaseModel(Model):
    class Meta:
        database = db


class Data(BaseModel):
    id = AutoField()
    tieude = CharField()
    mota = TextField()
    noidung = TextField()
    uri = CharField()


class Users(BaseModel):
    id = AutoField()
    email = CharField()
    password = CharField()


def add_table(name):
    name.create_table()
