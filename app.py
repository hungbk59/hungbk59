import model
import os
import jwt

from datetime import datetime, timedelta

from flask import Flask, jsonify, request
from flask_cors import CORS

from werkzeug.security import generate_password_hash, check_password_hash
from walrus import Walrus


app = Flask(__name__)
app.config['SECRET_KEY'] = 'Herocoders'
CORS(app, resources={r"/data/*": {"origins": "*"}})

dbw = Walrus(host='127.0.0.1', port=6379, db=0)
cache = dbw.cache()

data = model.Data
user = model.Users


def check_character(character):
    """Danh sách các ký tự không mong muốn"""
    special = '''`~!#$%^&*()_=+-*/\[]{}|:;<>'"?'''
    for i in range(len(special)):
        if character is special[i]:
            return 0
    return 1


def loc(char):
    """Danh sách các ký tự loại bỏ"""
    special = '''`~!#$%^&*()_=+-*/\[]{}|:;<>'"?'''
    for i in range(len(special)):
        char = char.replace(special[i], '')
    return char


def filters(char):
    for i in range(len(char)):
        if check_character(char[i]) == 0:
            return 0
    return 1


@app.route("/data/search", methods=["GET"])
@cache.cached(timeout=10)
def get_search():
    tieude = request.args.get("tieude", type=str)
    noidung = request.args.get("noidung", type=str)
    news = []
    sel = data.select()
    if filters(tieude) == 0 or filters(noidung) == 0:
        tieude = loc(tieude)
        noidung = loc(noidung)
    if tieude == "" and noidung == "":
        return jsonify({"message": "Enter search content"})

    if tieude and noidung:
        new = sel.where(data.tieude ** ("%" + tieude + "%"),
                        data.noidung ** ("%" + noidung + "%")) \
            .dicts()
        for row in new:
            news.append(row)
        return jsonify({"list_news": news})

    if tieude:
        new = sel.where(data.tieude ** ("%" + tieude + "%"))\
            .dicts()
        for row in new:
            news.append(row)
        return jsonify({"list_news": news})

    elif noidung:
        new = sel.where(data.noidung ** ("%" + noidung + "%"))\
            .dicts()
        for row in new:
            news.append(row)
        return jsonify({"list_news": news})


@app.route("/data/search/<int:num>", methods=["GET"])
@cache.cached(timeout=10)
def get_search_id(num):
    if id == 0:
        return jsonify({"message": "Not exist ID"})
    else:
        sel = data.select()
        new = sel.where(data.id == num).dicts()
        for row in new:
            return jsonify({"list_news": row})


@app.route("/data/update", methods=["PUT", "POST"])
def update_data():
    _title = request.form["tieude"]
    _content = request.form["noidung"]
    _url = request.form["url"]

    # Kiểm tra dữ liệu nhập vào có hợp lệ
    if filters(_title) == 0 or filters(_content) == 0:
        return jsonify({"status": 401, "message": "Re-enter Data"})

    # Sửa tiêu đề và nội dung theo URI của bài báo
    if request.method == "PUT":
        check_url = data.select(data.uri).where(data.uri == _url).count()
        if check_url == 0:
            return jsonify({"status": 404, "message": "Not exist News"})
        else:
            (data
             .update(tieude=_title, noidung=_content)
             .where(data.uri == _url).execute())

            return jsonify({"status": 200, "message": "Update Successfull"})

    # Thêm tiêu đề và nội dung của 1 bài báo mới
    elif request.method == "POST":
        (data
         .insert(tieude=_title, noidung=_content, uri=_url)
         .execute())

        return jsonify({"status": 200, "message": "Insert Successfull"})


@app.route("/data/delete/<int:num>", methods=["DELETE"])
def delete_data(num):
    data.delete().where(data.id == num).execute()
    return jsonify({"status": 200, "message": "Delete Successfull"})


@app.route("/data/login", methods=["POST"])
def login():
    _email = request.form["email"]
    _password = request.form["password"]
    check_email = (user
                   .select()
                   .where(user.email == _email)
                   .count())
    if check_email == 1:
        query = user.select()\
            .where(user.email == _email).dicts()

        for row in query:
            password = row["password"]
            if row:
                if check_password_hash(password, _password):
                    token = jwt.encode({
                        'email': _email,
                        'exp': datetime.utcnow() + timedelta(minutes=60)},
                        app.config['SECRET_KEY'])
                    return jsonify({
                        "status": 200,
                        "message": "logged in successfully",
                        "token": token})
                else:
                    return jsonify({"status": 404,
                                    "message": "Bad Request - invalid credentials"})
    else:
        return jsonify({"status": 404,
                        "message": "Bad Request - invalid credentials"})


@app.route('/data/register', methods=["POST"])
def register():
    _email = request.form["email"]
    _password = request.form["password"]
    _retype_password = request.form["re_password"]
    if filters(_email) == 0 or filters(_password) == 0:
        return jsonify({"status": 401, "message": "Re-enter Data"})
    if _retype_password != _password:
        return jsonify({"status": 400, "message": "re-password incorrect"})
    check_email = (user
                   .select()
                   .where(user.email == _email)
                   .count())
    if check_email == 0:
        _password_hash = generate_password_hash(_password)
        (user
         .insert(email=_email, password=_password_hash)
         .execute())
        return jsonify({"status": 200, "message": "Register in successfully"})
    else:
        return jsonify({"status": 404, "message": "email already exist"})


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


if __name__ == '__main__':
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    app.run(HOST, 8000)
