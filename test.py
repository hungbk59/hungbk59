import requests
import schedule
import time
from bs4 import BeautifulSoup
from peewee import (MySQLDatabase, Model, TextField)
#tạo database
db = MySQLDatabase('test', user='admin', password='abc123')
mycursor = db.cursor()

link_base = "https://vnexpress.net/giao-duc"
list_link = []
print('nhập số lượng page:')
page = int(input())

def scrape():
    for num in range(1, page):
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
                contents = ''
            except:
                title = ""
                decript = ""
                contents = ""

            for content in body:
                contents += ' ' + content.text

            class data(Model):
                tieude = TextField()
                mota = TextField()
                noidung = TextField()

                class Meta:
                    database = db
                    db_table = 'data'

            data.create_table()
            check_data = data.select(data.tieude).where(data.tieude==title).count()
            if check_data ==0:
                query = data.insert(tieude=title, mota=decript, noidung=contents).execute()

schedule.every().day.at("17:45").do(scrape)

#kiểm tra schedule
while True:
    schedule.run_pending()
    time.sleep(1)
