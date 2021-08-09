import requests
from bs4 import BeautifulSoup
import peewee
from peewee import MySQLDatabase
#tạo database
db = MySQLDatabase ('test', user='admin', password='abc123')
mycursor = db.cursor()
#xóa table database
try:
  mycursor.execute("DROP TABLE data ")
  print("Delete table database")
except:
  print("Not exist table database")

link_base = "https://vnexpress.net/giao-duc"
list_link = []
print('nhập số lượng page:')
page = int(input()) #số (n-1) trang muốn lấy thông tin
for num in range(1,page):
    list_link.append(link_base + '-p' + str(num))
for i in range(len(list_link)):
    link_page = list_link[i]
    r = requests.get(link_page)
    soup = BeautifulSoup(r.content, "html.parser")
    titles = soup.findAll('h3', class_='title-news')
    links = [link.find('a').attrs["href"] for link in titles]
    for link in links:
        news = requests.get(link)
        soup = BeautifulSoup(news.content, "html.parser")

        try:
            title = soup.find("h1", class_="title-detail").text.strip()
            decript = soup.find("p", class_="description").text.strip()
            body = soup.find_all('p', class_='Normal')
            contents =''
            for content in body:
                contents += ' ' + content.text
        except:
            title = ""
            decript = ""
            contents = ""

        class data(peewee.Model):
            tieude = peewee.TextField()
            mota = peewee.TextField()
            noidung = peewee.TextField()

            class Meta:
                database = db
        data.create_table()
        Data = data(tieude=title, mota=decript, noidung=contents)
        Data.save()
