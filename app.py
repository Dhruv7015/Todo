from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import json, os
from datetime import date
from flask_mail import Mail


with open("config.json", "r") as c:
    params = json.load(c)["params"]

server = params["server_local"]
app = Flask(__name__)
app.config.update(
    MAIL_SERVER="smtp.gmail.com",
    MAIL_PORT="465",
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params["gmail_user"],
    MAIL_PASSWORD=params["gmail_password"],
)
mail = Mail(app)
app.secret_key = "super-secret-key"
if server == False:
    app.config["SQLALCHEMY_DATABASE_URI"] = params["main_uri"]
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = params["main_uri"]

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Todo(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(1000), nullable=False)
    date_created = db.Column(db.Date, default=date.today())


@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        title = request.form["title"]
        desc = request.form["desc"]
        name = request.form["name"]
        if title != "" and desc != "" and name != "":
            todo = Todo(title=title, desc=desc, name=name)
            # mail.send_message(
            #     "MyThought - Message From " + name,
            #     sender=params["gmail_user"],
            #     recipients=[params["gmail_user"]],
            #     body="A thought has been added by :- "
            #     + name
            #     + "\n"
            #     + "Thought :- "
            #     + desc,
            # )
            db.session.add(todo)
            db.session.commit()
    allTodo = Todo.query.all()
    return render_template("index.html", allTodo=allTodo)


@app.route("/login", methods=["POST", "GET"])
def login():
    alltodo = Todo.query.all()
    if "user" in session and session["user"] == params["admin_user"]:
        return render_template("dashboard.html", alltodo=alltodo)
    elif request.method == "POST":
        usern = request.form.get("username")
        userp = request.form.get("password")
        if usern == params["admin_user"] and userp == params["admin_password"]:
            session["user"] = usern
            return render_template("dashboard.html", alltodo=alltodo)
    return render_template("login.html")


@app.route("/update/<int:sno>", methods=["POST", "GET"])
def update(sno):
    if request.method == "POST":
        title = request.form["title"]
        desc = request.form["desc"]
        todo = Todo.query.filter_by(sno=sno).first()
        todo.title = title
        todo.desc = desc
        db.session.add(todo)
        db.session.commit()
        return redirect("/")
    todo = Todo.query.filter_by(sno=sno).first()
    return render_template("update.html", todo=todo)


@app.route("/delete/<int:sno>")
def delete(sno):
    todo = Todo.query.filter_by(sno=sno).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect("/login")


@app.route("/logout")
def logut():
    session.pop("user")
    return redirect("/login")


@app.route("/about", methods=["POST", "GET"])
def aboout():
    return render_template("about.html")


if __name__ == "__main__":
    if not os.path.isdir("db"):
        os.mkdir("db")
        from app import db

        db.create_all()
    else:
        pass
    app.run(debug=server)
