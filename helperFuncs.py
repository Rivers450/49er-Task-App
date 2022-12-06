from flask import session
from database import db
from models import User as User

# switches modes to input
def mode_switch(mode):
    # list of files to change
    for file in ["forms", "main"]:
        with open("static\\mode{0}\\{1}{0}.css".format(mode, file)) as input:
            with open("static\\{0}.css".format(file), "w") as output:
                output.write(input.read())


def getCurrentUser():
    current_user_id = session["user_id"]
    user = db.session.query(User).filter_by(id=current_user_id).one()
    return user


# TODO: general delete (delete comment)
