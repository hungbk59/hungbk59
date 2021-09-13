import requests
import models
import schedule
import time
from bs4 import BeautifulSoup

def crwal():
    link_base = "https://vnexpress.net/giao-duc"
    check_page = ""

    while check_page != "javascript:;":

        r = requests.get(link_base)
        soup = BeautifulSoup(r.content, "html.parser")
        titles = soup.findAll('h3', class_='title-news')
        links = [link.find('a').attrs["href"] for link in titles]

        for link in links:
            news = requests.get(link)
            soup_news = BeautifulSoup(news.content, "html.parser")
            contents = ""
            try:
                title = soup_news.find("h1", class_="title-detail").text.strip()
                decript = soup_news.find("p", class_="description").text.strip()
                body = soup_news.find_all('p', class_='Normal')
            except:
                title = ""
                decript = ""
                body = ""

            for content in body:
                contents += ' ' + content.text

            data = models.database()
            check_data = data.select(data.mota).where(data.mota == decript).count()
            # Kiểm tra sự tồn tại của bài báo
            if check_data == 0:
                query = data.insert(tieude=title, mota=decript, noidung=contents).execute()
            elif check_data >0:
                break

        # Kiểm tra các link page tiếp theo
        link_next = soup.findAll('a', class_='btn-page next-page')
        link_end = soup.findAll('a', class_='btn-page next-page disable')
        for link_end_tail in link_end:
            check_page = link_end_tail.get('href')

        # Lấy ra href của trang tiếp theo
        for link_tail in link_next:
            link_page = "https://vnexpress.net" + link_tail.get('href')
            link_base = link_page

schedule.every().day.at("17:00").do(crwal)

# Kiểm tra schedule
while True:
    schedule.run_pending()
    time.sleep(1)