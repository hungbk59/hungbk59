import requests
import time
from multiprocessing import Process, Queue

def get_link(link_base,q):
    csc = 0  # Check status code
    num = 1399  # Number page
    while csc != 302:
        num += 1
        link_page = link_base + '-p' + str(num)
        r = requests.get(link_page)
        check_redirect = r.history
        q.put(link_page)  # Đưa dữ liệu vào hàng chờ
        for stc in check_redirect:
            csc = stc.status_code

def crawl(q):
    number=1
    while not q.empty():
        print("link page",number,' ',q.get())
        number +=1

def main():

    p1 = Process(target=crawl, args=(q,))
    p1.start()

    p2 = Process(target=crawl, args=(q,))
    p2.start()

    p1.join()
    p2.join()

if __name__ == '__main__':
    start_time = time.time()

    q = Queue()
    get_link('https://vnexpress.net/giao-duc',q)
    main()

    end_time = time.time()
    elapsed_time = end_time - start_time
    print("Thời gian Run: {0}".format(elapsed_time) + "[sec]")