import requests
import models
from bs4 import BeautifulSoup
from multiprocessing import Process, Queue

# Hàm lấy ra danh sách link page
def get_link(link_base,q):
    csc = 0  # Check status code
    num = 0  # Number page
    while csc != 302:
        num += 1
        link_page = link_base + '-p' + str(num)
        r = requests.get(link_page, allow_redirects=False)
        csc = r.status_code
        q.put(link_page)

    q.put("KETTHUC")
    q.put("KETTHUC")
    q.put("KETTHUC")
    q.put("KETTHUC")

# Hàm cào dữ liệu link bài báo, lưu và check dữ liệu trong database
def crwal(q):
    while True:
        link_page = q.get()
        if link_page == "KETTHUC":
            break
        print(link_page)
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

def main(q):
    p1_crawl = Process(target=crwal, args=(q,))
    p1_crawl.start()

    p2_crawl = Process(target=crwal, args=(q,))
    p2_crawl.start()

    p3_crawl = Process(target=crwal, args=(q,))
    p3_crawl.start()

    p4_crawl = Process(target=crwal, args=(q,))
    p4_crawl.start()

    p1_crawl.join()
    p2_crawl.join()
    p3_crawl.join()
    p4_crawl.join()

    print('Kết thúc')

if __name__ == "__main__":
    link_base = 'https://vnexpress.net/giao-duc'
    q = Queue()
    p_getlink = Process(target=get_link, args=(link_base,q,))
    p_getlink.start()
    
    main(q)
    
    p_getlink.join()
