import requests
import models
import schedule
import time
from bs4 import BeautifulSoup
from multiprocessing import Process

# Hàm lấy ra danh sách link page
def get_link(link_base):
    list_link = []
    link_page = link_base
    csc = 0  # Check status code
    num = 0  # Number page
    while csc != 302:
        num += 1
        list_link.append(link_page)
        link_page = link_base + '-p' + str(num)
        r = requests.get(link_page)
        check_redirect = r.history

        for stc in check_redirect:
            csc = stc.status_code
    return list_link

# Hàm cào dữ liệu link bài báo, lưu và check dữ liệu trong database
def crwal(list_link):

    for L in range(len(list_link)):
        link_page = list_link[L]
        r = requests.get(link_page)
        r = requests.get(link_page)
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
            check_link = data.select(data.https).where(data.https == link).count()

            # Kiểm tra sự trung lặp của link
            if check_link == 0:
                query = data.insert(tieude=title, mota=decript, noidung=contents, https=link).execute()
            else:
                break

def main():
    p = Process(target=crwal, args=(get_link('https://vnexpress.net/giao-duc'),))
    p.start()
    p.join()
def run ():
    if __name__ == "__main__":
        main()

schedule.every().day.at("17:00").do(run)

# Kiểm tra schedule
while True:
    schedule.run_pending()
    time.sleep(1)
