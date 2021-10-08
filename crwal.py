import requests
import model
from bs4 import BeautifulSoup
from multiprocessing import Process, Queue

data = model.Data


def get_link(links_base, queue):
    csc = 0  # Check status code
    num = 0  # Number page
    while csc != 302:
        num += 1
        link_page = links_base + '-p' + str(num)
        r = requests.get(link_page, allow_redirects=False)
        csc = r.status_code
        queue.put(link_page)

    queue.put("KETTHUC")
    queue.put("KETTHUC")
    queue.put("KETTHUC")
    queue.put("KETTHUC")


def scrape(queue):
    while True:
        link_page = queue.get()
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
            except soup_news:
                title = ""
                decript = ""
                body = ""

            for content in body:
                contents += ' ' + content.text

            check_link = data.select(data.uri).where(data.uri == link).count()

            # Kiểm tra sự trung lặp của link
            if check_link == 0:
                data.insert(tieude=title, mota=decript, noidung=contents, uri=link).execute()
            else:
                break


def main(queue):
    for i in range(1, 5):
        pi_crawl = Process(target=scrape, args=(queue,))
        pi_crawl.start()
    for i in range(1, 5):
        pi_crawl.join()


if __name__ == "__main__":
    link_base = 'https://vnexpress.net/giao-duc'
    q = Queue()
    p_getlink = Process(target=get_link, args=(link_base, q,))
    p_getlink.start()
    main(q)
    p_getlink.join()
