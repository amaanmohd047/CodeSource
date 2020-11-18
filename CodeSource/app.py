from flask import (
    Flask, 
    render_template, 
    request, 
    redirect, 
    session, 
    url_for
    )
from datetime import datetime
import json
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
import os

with open("config.json", 'r') as config:
    configs = json.load(config)["configs"]

app = Flask(__name__)

db = SQLAlchemy(app)

local_server = True

random_key = os.urandom(20)
app.secret_key = random_key

if local_server:
    app.config['SQLALCHEMY_DATABASE_URI'] = configs["local_uri"]
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = configs["production_uri"]

app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = 'configs["gmail_username"]',
    MAIL_PASSWORD = 'configs["gmail_password"]'
)

mail = Mail(app)

app.debug = True

local_server = True

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sender = db.Column(db.String(99), nullable=False)
    email = db.Column(db.String(99), nullable=False)
    body = db.Column(db.String(999), nullable=False)


class Entries(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(99), nullable=False)
    extension = db.Column(db.String(5), nullable=False)
    code = db.Column(db.String(999999), nullable=False)
    created = db.Column(db.DateTime, nullable=False)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template("index.html")

@app.route('/view/<string:id>')
def view(id):
    entry = Entries.query.filter_by(id=id).first()
    return render_template("view.html", entry=entry)


@app.route('/pythonpage')
def pythonpage():
    py_ent = Entries.query.filter_by(extension=".py").all()
    return render_template("python.html", py_ent=py_ent)


@app.route('/cpp')
def cpp():
    cpp_ent = Entries.query.filter_by(extension=".cpp").all()
    return render_template("c++.html", cpp_ent=cpp_ent)


@app.route('/js')
def javascript():
    js_ent = Entries.query.filter_by(extension=".js").all()
    return render_template("javascript.html", js_ent=js_ent)


@app.route('/web')
def web():
    return render_template("webdev.html")


@app.route('/mobile')
def mobiledev():
    return render_template("mobiledev.html")


@app.route('/game')
def gamedev():
    return render_template("gamedev.html")

@app.route('/dashboard', methods=["GET", "POST"])
def dashboard():
    entries = Entries.query.all()
    if 'username' in session and session['username'] == configs["admin_username"]:
        return render_template("list.html", entries=entries)

    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        admin_username = configs["admin_username"]
        admin_password = configs["admin_password"]

        if (username == admin_username) and (password == admin_password):
            session['username'] = username
            return render_template("list.html", entries=entries)
        else:
            return redirect(url_for('index'))
    else:
        return render_template("admin-login.html")


@app.route('/logout', methods=["GET"])
def logout():
    if 'username' in session and session['username'] == configs["admin_username"]:
        session.pop('username')
        return redirect(url_for('dashboard'))
    return render_template(url_for('dashboard'))


@app.route('/delete/<string:id>', methods=["GET"])
def delete(id):
    if 'username' in session and session['username'] == configs["admin_username"]:
        entry = Entries.query.filter_by(id=id).first()
        db.session.delete(entry)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template(url_for('dashboard'))


@app.route('/admin-search', methods=["POST"])
def admin_search():
    if 'username' in session and session['username'] == configs["admin_username"]:        
        if request.method == "POST":
            search_title = request.form.get('title')

            search_result = Entries.query.filter(Entries.title.contains(search_title)).all()
            search_count = Entries.query.filter(Entries.title.contains(search_title)).count()

            return render_template("admin-search.html", search_result=search_result, search_title=search_title)


@app.route('/add-python', methods=["GET"])
def add_py():
    if 'username' in session and session['username'] == configs["admin_username"]:
        ext = ".py"
        return render_template("add.html", ext=ext)
    else:
        return render_template("admin-login.html")


@app.route('/add-js', methods=["GET"])
def add_js():    
    if 'username' in session and session['username'] == configs["admin_username"]:
        ext = ".js"
        return render_template("add.html", ext=ext)
    else:
        return render_template("admin-login.html")


@app.route('/add-cpp', methods=["GET"])
def add_cpp():
    if 'username' in session and session['username'] == configs["admin_username"]:
        ext = ".cpp"
        return render_template("add.html", ext=ext)
    else:
        return render_template("admin-login.html")


@app.route('/post', methods=["POST"])
def post():
    date = datetime.now()
    if 'username' in session and session['username'] == configs["admin_username"]:
        if request.method == "POST":
            title = request.form.get('title')
            code = request.form.get('code')
            extension = request.form.get('extension')
            file_title = title + extension
            created = datetime.now()

            entry = Entries(title=file_title, 
                            code=code, 
                            extension=extension,
                            created=created
                            )
            db.session.add(entry)
            db.session.commit()
            return redirect(url_for('dashboard'))
    
    else:
        return render_template("admin-login.html")


@app.route('/add-web', methods=["GET", "POST"])
def add_web():
    if 'username' in session and session['username'] == configs["admin_username"]:
        if request.method == "POST":
            title = request.form.get('title')
            code = request.form.get('code')
            extension = rewuest.form.get('extexsion')
    
        return render_template("add-web.html")


@app.route('/code/<string:id>', methods=['GET'])
def detail_route(id):
    entry = Entries.query.filter_by(id=id).first()
    return render_template("detail.html", entry=entry)


@app.route('/edit/<string:id>', methods=["GET", "POST"])
def edit_route(id):
    if 'username' in session and session['username'] == configs["admin_username"]:
        if request.method == "POST":
            entry = Entries.query.filter_by(id=id).first()
            
            title = request.form.get('title')
            code = request.form.get('code')

            entry.title = title
            entry.code = code

            db.session.commit()

            return redirect(url_for('dashboard'))
            

        
        else:
            entry = Entries.query.filter_by(id=id).first()
            return render_template("edit.html", entry=entry)


@app.route('/search', methods=["POST"])
def search():
    if request.method == "POST":
        search_title = request.form.get('title')

        search_result = Entries.query.filter(Entries.title.contains(search_title)).all()
        search_count = Entries.query.filter(Entries.title.contains(search_title)).count()

        if search_count == 0:
            return render_template("nomatch.html")

        return render_template("search.html", search_result=search_result, search_title=search_title)


@app.route('/contacts', methods=["GET", "POST"])
def contacts():
        if request.method == "POST":
            sender = request.form.get('name')
            email = request.form.get('email')
            body = request.form.get('message')

            message = Contact(sender=sender, email=email, body=body)
            db.session.add(message)
            db.session.commit()
            try:
                mail.send_message('An email from' + sender,
                sender = email,
                recipients = configs["gmail_username"],
                body = body
                )
                return redirect(url_for('index'))
            except:
                print("There was an error sending email.")
                return redirect(url_for('index'))
        
        if 'username' in session and session['username'] == configs["admin_username"]:
            if request.method == "GET":
                messages = Contact.query.all()
                return render_template("contacts.html", messages=messages)    
        
        return render_template("index.html")


@app.route('/message/<string:id>')
def view_message(id):
    message = Contact.query.filter_by(id=id).first()
    return render_template("view-message.html", message=message)


@app.route('/delete-message/<string:id>')
def delete_message(id):
    if 'username' in session and session['username'] == configs["admin_username"]:
        message = Contact.query.filter_by(id=id).first()
        db.session.delete(message)
        db.session.commit()
        return redirect(url_for('contacts'))
    return render_template(url_for('dashboard'))


if __name__ == '__main__':
    app.run()