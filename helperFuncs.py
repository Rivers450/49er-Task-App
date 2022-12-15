from flask import session
from database import db
from models import User as User
import matplotlib.pyplot as plt
import io
from PIL import Image, ImageChops
import numpy as np

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


def renderLatex(latexString, filepath="static\\latex.png"):
    # Based on code from Andrew Slabko on stackoverflow
    # https://stackoverflow.com/a/50168210

    white = (255, 255, 255, 255)

    buf = io.BytesIO()
    plt.rc("text")
    plt.rc("font", family="serif")
    plt.axis("off")
    plt.text(0.05, 0.5, latexString, size=15)
    plt.savefig(filepath)
    plt.close()
    return


def cropImage(filepath="static\\latex.png"):
    # Based on code from Gareth Rees on codereview.stackexchange
    # https://codereview.stackexchange.com/a/132933

    img = Image.open(filepath)
    img = img.convert("L")  # convert to single channel image
    image = np.asarray(img)  # converting image to numpy array

    # Mask of non-white pixels
    mask = image < 127

    # Coordinates of non-white pixels.
    coords = np.argwhere(mask)

    # Bounding box of non-white pixels.
    x0, y0 = coords.min(axis=0)
    x1, y1 = coords.max(axis=0) + 1  # slices are exclusive at the top

    # Get the contents of the bounding box.
    Image.fromarray(image[x0:x1, y0:y1]).save(filepath)
    return


def invertImage(filepath="static\\latex.png"):
    img = Image.open(filepath)
    img = img.convert("L")  # convert to single channel image
    image = np.asarray(img)  # converting image to numpy array
    image = 255 - image
    Image.fromarray(image).save(filepath)


# TODO: general delete (delete comment)
