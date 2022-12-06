from database import db
import datetime


class User(db.Model):
    id = db.Column("id", db.Integer, primary_key=True)
    first_name = db.Column("first_name", db.String(100))
    last_name = db.Column("last_name", db.String(100))
    email = db.Column("email", db.String(100))
    password = db.Column(db.String(255), nullable=False)
    # 0 is dark mode, 1 is light mode
    view_mode = db.Column("view_mode", db.Integer, default=0, nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    notes = db.relationship(
        "Note", backref="user", cascade="all, delete-orphan", lazy=True
    )

    def __init__(self, first_name, last_name, email, password, view_mode):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.registered_on = datetime.date.today()
        self.view_mode = view_mode


class Note(db.Model):
    id = db.Column("id", db.Integer, primary_key=True)
    title = db.Column("title", db.String(200))
    text = db.Column("text", db.String(100))
    date = db.Column("date", db.String(50))
    # 0 is false, 1 is true
    uses_latex = db.Column(db.Integer, default=0, nullable=False)
    # can create a foreign key; referencing the id variable in the User class, so that is why it is lowercase u
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    comments = db.relationship(
        "Comment", backref="note", cascade="all, delete-orphan", lazy=True
    )

    def __init__(self, title, text, date, uses_latex, user_id):
        self.title = title
        self.text = text
        self.date = date
        self.user_id = user_id
        self.uses_latex = uses_latex


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False)
    content = db.Column(db.VARCHAR, nullable=False)
    note_id = db.Column(db.Integer, db.ForeignKey("note.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __init__(self, content, note_id, user_id):
        self.date_posted = datetime.date.today()
        self.content = content
        self.note_id = note_id
        self.user_id = user_id
