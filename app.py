import models
from flask import Flask, jsonify, request, session
from werkzeug.security import generate_password_hash

app = Flask(__name__)
data = models.Data
user = models.Users
app.secret_key = generate_password_hash('Herocoders')


def check_character(character):
    """Danh sách các ký tự không mong muốn"""
    special = '''`~!@#$%^&*()_-=+-*/\[]{}|:;<>'"?'''
    for i in range(len(special)):
        if character is special[i]:
            return 0
    return 1


def loc(char):
    """Danh sách các ký tự loại bỏ"""
    special = '''`~!@#$%^&*()_-=+-*/\[]{}|:;<>'"?'''
    for i in range(len(special)):
        char = char.replace(special[i], '')
    return char


def filters(char):
    """Kiểm tra từng phần tử trong chuỗi"""
    for i in range(len(char)):
        if check_character(char[i]) == 0:
            return 0
    return 1


@app.route("/data/search", methods=["GET"])
def get_search():
    """Tìm kiếm bài báo theo tiêu đề, nội dung với kết quả tìm kiếm được giới hạn""" 
    tieude = request.args.get("tieude", type=str)
    noidung = request.args.get("noidung", type=str)
    page = request.args.get("page", type=int)
    limit = request.args.get("limit", type=int)

    if filters(tieude) == 0 or filters(noidung) == 0:
        tieude = loc(tieude)
        noidung = loc(noidung)

    new = (data
           .select()
           .where(data.tieude ** ("%" + tieude + "%"), data.noidung ** ("%" + noidung + "%"))
           .limit(limit).offset(page)
           .dicts())
    news = []

    for row in new:
        news.append(row)
    return jsonify({"list_news": news})


@app.route("/data/update", methods=["PUT", "POST"])
def update_data():
    # Kiểm tra trang thái login
    if 'email' in session:
        _title = request.form["tieude"]
        _content = request.form["noidung"]

        # Kiểm tra dữ liệu nhập vào có hợp lệ
        if filters(_title) == 0 or filters(_content) == 0:
            return jsonify({"status": -2, "message": "Re-enter Data"})

        # Sửa tiêu đề và nội dung theo URI của bài báo
        if request.method == "PUT":
            (data
             .update(tieude=_title, noidung=_content)
             .where(data.uri == request.form["uri"]).execute())

            return jsonify({"status": 1, "message": "Update Successfull"})

        # Thêm tiêu đề và nội dung của 1 bài báo mới
        elif request.method == "POST":
            (data
             .insert(tieude=_title, noidung=_content)
             .execute())

            return jsonify({"status": 1, "message": "Insert Successfull"})
    else:
        resp = jsonify({'message': 'Unauthorized'})
        resp.status_code = 401
        return resp


@app.route("/data/delete%<int:new_id>", methods=["DELETE"])
def delete_data():
    # Kiểm tra trang thái login
    if 'email' in session:
        data.delete().where(data.uri == request.form["uri"]).execute()
        return jsonify({"status": 1, "message": "Delete Successfull"})
    else:
        resp = jsonify({'message': 'Unauthorized'})
        resp.status_code = 401
        return resp


@app.route("/login", methods=["POST"])
def login():
    """Đăng nhập email/password và xác thực email/password đó"""
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


if __name__ == '__main__':
    app.run(debug=True)
