import os  # os is used to get environment variables IP & PORT
from flask import Flask  # Flask is the web app that we will customize
from flask import render_template
from flask import request
from flask import redirect, url_for
from database import db
from models import Note as Note
from models import User as User
from forms import RegisterForm
from flask import session
from forms import LoginForm
import bcrypt
from models import Comment as Comment
from forms import RegisterForm, LoginForm, CommentForm
import sympy
import helperFuncs as help
from sqlalchemy import exc

app = Flask(__name__)  # create an app
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sweDatabase.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["SECRET_KEY"] = "SE3155"

db.init_app(app)
with app.app_context():
    db.create_all()

# @app.route is a decorator. It gives the function "index" special powers.
# In this case it makes it so anyone going to "your-url/" makes this function
# get called. What it returns is what is shown as the web page
@app.route("/")
@app.route("/home")
def index():
    try:
        if session.get("user"):
            user = help.getCurrentUser()
            return render_template("home.html", user=user)
    except exc.NoResultFound:
        return redirect(url_for("logout"))
    return render_template("home.html")


@app.route("/notes")
def get_notes():
    if session.get("user"):
        user = help.getCurrentUser()

        my_notes = db.session.query(Note).filter_by(user_id=user.id).all()

        return render_template("notes.html", notes=my_notes, user=user)
    else:
        return redirect(url_for("login"))


@app.route("/notes/<note_id>")
def get_note(note_id):
    if session.get("user"):
        user = help.getCurrentUser()
        my_note = db.session.query(Note).filter_by(id=note_id, user_id=user.id).one()

        form = CommentForm()

        sympy.preview(
            my_note.text,
            viewer="file",
            filename="static\\latex.png",
            euler=False,
        )

        return render_template(
            "note.html",
            note=my_note,
            user=user,
            form=form,
            latex=my_note.uses_latex,
        )
    else:
        return redirect(url_for("login"))


@app.route("/notes/new", methods=["GET", "POST"])
def new_note():
    if session.get("user"):
        user = help.getCurrentUser()

        if request.method == "POST":
            title = request.form["title"]
            text = request.form["noteText"]
            latex = request.form.get("latex")
            if latex == "1":
                latex = 1
            else:
                latex = 0
            print(latex)

            from datetime import date

            today = date.today()

            today = today.strftime("%Y-%m-%d")
            new_record = Note(title, text, today, latex, user.id)
            db.session.add(new_record)
            db.session.commit()

            return redirect(url_for("get_notes"))
        else:
            return render_template("new.html", user=user)
    else:
        return redirect(url_for("login"))


@app.route("/notes/edit/<note_id>", methods=["GET", "POST"])
def update_note(note_id):
    if session.get("user"):
        user = help.getCurrentUser()

        if request.method == "POST":

            title = request.form["title"]
            text = request.form["noteText"]
            note = db.session.query(Note).filter_by(id=note_id).one()
            note.title = title
            note.text = text

            latex = request.form.get("latex")
            if latex == "1":
                latex = 1
            else:
                latex = 0
            note.uses_latex = latex

            db.session.add(note)
            db.session.commit()

            return redirect(url_for("get_notes"))
        else:
            my_note = db.session.query(Note).filter_by(id=note_id).one()
            return render_template("new.html", note=my_note, user=user)
    else:
        return redirect(url_for("login"))


@app.route("/notes/delete/<note_id>", methods=["POST"])
def delete_note(note_id):
    # retrieve note from database
    if session.get("user"):
        user = help.getCurrentUser()

        my_note = db.session.query(Note).filter_by(id=note_id).one()
        db.session.delete(my_note)
        db.session.commit()
        return redirect(url_for("get_notes"))
    else:
        return redirect(url_for("login"))


@app.route("/register", methods=["POST", "GET"])
def register():
    form = RegisterForm()

    if request.method == "POST" and form.validate_on_submit():
        # salt and hash password
        h_password = bcrypt.hashpw(
            request.form["password"].encode("utf-8"), bcrypt.gensalt()
        )
        # get entered user data
        first_name = request.form["firstname"]
        last_name = request.form["lastname"]
        # create user model
        new_user = User(first_name, last_name, request.form["email"], h_password, 0)
        # add user to database and commit
        db.session.add(new_user)
        db.session.commit()
        # save the user's name to the session
        session["user"] = first_name
        session[
            "user_id"
        ] = new_user.id  # access id value from user model of this newly added user
        # show user dashboard view
        return redirect(url_for("get_notes"))

    # something went wrong - display register view
    return render_template("register.html", form=form)


@app.route("/login", methods=["POST", "GET"])
def login():
    login_form = LoginForm()
    # validate_on_submit only validates using POST
    if login_form.validate_on_submit():
        # we know user exists. We can use one()
        the_user = db.session.query(User).filter_by(email=request.form["email"]).one()
        # user exists check password entered matches stored password
        if bcrypt.checkpw(request.form["password"].encode("utf-8"), the_user.password):
            # password match add user info to session
            session["user"] = the_user.first_name
            session["user_id"] = the_user.id
            # render view
            return redirect(url_for("get_notes"))

        # password check failed
        # set error message to alert user
        login_form.password.errors = ["Incorrect username or password."]
        return render_template("login.html", form=login_form)
    else:
        # form did not validate or GET request
        return render_template("login.html", form=login_form)


@app.route("/logout")
def logout():
    # check if a user is saved in session
    if session.get("user"):
        session.clear()
        help.mode_switch(0)

    return redirect(url_for("index"))


@app.route("/notes/<note_id>/comment", methods=["POST"])
def new_comment(note_id):
    if session.get("user"):
        user = help.getCurrentUser()
        comment_form = CommentForm()
        # validate_on_submit only validates using POST
        if comment_form.validate_on_submit():
            # get comment data
            comment_text = request.form["comment"]
            new_record = Comment(comment_text, int(note_id), user.id)
            db.session.add(new_record)
            db.session.commit()

        return redirect(url_for("get_note", note_id=note_id))

    else:
        return redirect(url_for("login"))


@app.route("/contactUs")
def contact():
    return render_template("contactUs.html")


@app.route("/success")
def success():
    return render_template("success.html")


@app.route("/account")
def account():
    if session.get("user"):
        user = help.getCurrentUser()

        return render_template("account.html", user=user)
    return redirect(url_for("login"))


@app.route("/account/delete", methods=["GET", "POST"])
def delete_account():
    if session.get("user"):
        user = help.getCurrentUser()

        # Delete comments, notes, and user
        db.session.query(Comment).filter_by(user_id=user.id).delete()
        db.session.query(Note).filter_by(user_id=user.id).delete()
        db.session.query(User).filter_by(id=user.id).delete()

        db.session.commit()
        session.clear()
        return redirect(url_for("index"))
    else:
        return redirect(url_for("login"))


@app.route("/account/mode", methods=["GET", "POST"])
def change_mode():
    if session.get("user"):
        user = help.getCurrentUser()

        user = db.session.query(User).filter_by(id=user.id).one()
        user.view_mode += 1
        # how many modes there are
        user.view_mode %= 2
        mode = user.view_mode

        help.mode_switch(mode)

        db.session.commit()
        return redirect(url_for("account"))
    else:
        return redirect(url_for("login"))


app.run(
    host=os.getenv("IP", "127.0.0.1"), port=int(os.getenv("PORT", 5000)), debug=True
)

# To see the web page in your web browser, go to the url,
#   http://127.0.0.1:5000

# Note that we are running with "debug=True", so if you make changes and save it
# the server will automatically update. This is great for development but is a
# security risk for production.
