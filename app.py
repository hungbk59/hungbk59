import requests
import models
from bs4 import BeautifulSoup
from multiprocessing import Process

# Hàm lấy ra danh sách link page
def get_link(link_base):
    list_link = []
    link_page = link_base
    csc = 0  # Check status code
    num = 1  # Number page
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
def crwal(head, last, list_link):
    for L in range(head, last):
        link_page = list_link[L]
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
    list_link = get_link('https://vnexpress.net/giao-duc')
    num_link = len(list_link)
    a = num_link // 4
    b = num_link // 2
    c = (3 * num_link) // 4

    p1 = Process(target=crwal, args=(0, a, list_link))
    p1.start()

    p2 = Process(target=crwal, args=(a, b, list_link))
    p2.start()

    p3 = Process(target=crwal, args=(b, c, list_link))
    p3.start()

    p4 = Process(target=crwal, args=(c, num_link, list_link))
    p4.start()

    p1.join()
    p2.join()
    p3.join()
    p4.join()

if __name__ == "__main__":
    main()
