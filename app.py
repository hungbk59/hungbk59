import requests
import models
from bs4 import BeautifulSoup
from multiprocessing import Process, Queue

from flask import Flask, jsonify, request, session
from werkzeug.security import generate_password_hash


data = models.Data
user = models.Users
app = Flask(__name__)
app.secret_key = generate_password_hash('Herocoders')


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

        
def check_character(character):
    """Danh sách các ký tự không mong muốn"""
    special = '''`~!@#$%^&*()_-=+-*/\[]{}|:;<>'"?'''
    for i in range(len(special)):
        if character is special[i]:
            return 0
    return 1


def filters(char):
    for i in range(len(char)):
        if check_character(char[i]) == 0:
            return 0
    return 1


@app.route("/data/search&page=<int:ph>&limit=<int:pe>", methods=["GET"])
def get_search(ph, pe):
    input_title = request.form["tieude"]
    input_content = request.form["noidung"]
    # Tìm kiếm dữ liệu theo tiêu đề và nội dung bài viết
    search_title = "%" + input_title + "%"
    search_content = "%" + input_content + "%"

    # Kiểm tra dữ liệu nhập vào có hợp lệ
    if filters(input_title) is False or filters(input_content) is False:
        return jsonify({"status": -2, "message": "Error input data"})

    if request.form.get("tieude") and request.form.get("noidung"):
        new = (data
               .select()
               .where(data.tieude ** search_title, data.noidung ** search_content)
               .limit(pe).offset(ph)
               .dicts())
        news = []

        for row in new:
            news.append(row)
        return jsonify({"list_news": news})
    return jsonify({"status": -1, "message": "Need add tieude or noidung"})


@app.route("/data/update", methods=["PUT", "POST"])
def update_data():
    if 'email' in session:
        input_title = request.form["tieude"]
        input_content = request.form["noidung"]

        # Kiểm tra dữ liệu nhập vào có hợp lệ
        if filters(input_title) is False or filters(input_content) is False:
            return jsonify({"status": -2, "message": "Error input data"})

        # Sửa tiêu đề và nội dung theo URI của bài báo
        if request.method == "PUT":
            (data
             .update(tieude=request.form["tieude"], noidung=request.form["noidung"])
             .where(data.uri == request.form["uri"]).execute())

            return jsonify({"status": 1, "message": "Update Successfull"})

        # Thêm tiêu đề và nội dung của 1 bài báo mới
        elif request.method == "POST":
            (data
             .insert(tieude=request.form["tieude"], noidung=request.form["noidung"])
             .execute())

            return jsonify({"status": 1, "message": "Insert Successfull"})
    else:
        resp = jsonify({'message': 'Unauthorized'})
        resp.status_code = 401
        return resp


@app.route("/data/delete%<int:new_id>", methods=["DELETE"])
def delete_data():
    if 'email' in session:
        data.delete().where(data.uri == request.form["uri"]).execute()
        return jsonify({"status": 1, "message": "Delete Successfull"})
    else:
        resp = jsonify({'message': 'Unauthorized'})
        resp.status_code = 401
        return resp


@app.route("/login", methods=["POST"])
def login():
    _email = request.form["email"]
    _password = request.form["password"]
    if request.form.get("email") and request.form.get("password"):
        query = (user
                 .select()
                 .where(user.email == _email, user.password == _password)
                 .count())
        if query == 1:
            session['email'] = _email
            return jsonify({"status": 1, "message": "logged in successfully"})
        else:
            return jsonify({"status": -1, "message": "Bad Request - invalid credentials"})

    else:
        return jsonify({"status": -1, "message": "Bad Request - invalid credentials"})


@app.route('/logout')
def logout():
    if 'email' in session:
        session.pop('email', None)
    return jsonify({'message': 'You successfully logged out'})


@app.errorhandler(400)
def handl_400_error(_error):
    return jsonify({"status": 400, "message": "Misunderstood"})


@app.errorhandler(401)
def handl_401_error(_error):
    return jsonify({"status": 401, "message": "Unauthorised"})


@app.errorhandler(404)
def handl_404_error(_error):
    return jsonify({"status": 404, "message": "Not found"})


@app.errorhandler(500)
def handl_500_error(_error):
    return jsonify({"status": 500, "message": "Server error"})


if __name__ == "__main__":
    link_base = 'https://vnexpress.net/giao-duc'
    q = Queue()
    p_getlink = Process(target=get_link, args=(link_base, q,))
    p_getlink.start()
    main(q)
    p_getlink.join()
    
    app.run(debug=True)
