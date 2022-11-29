import sympy

string = "hello, this is a note"
# raw_text = r"{}".format(string)
sympy.printing.preview(string, viewer="file", filename="test.png")
