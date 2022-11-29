import sympy

string = "hello, this is a note"
sympy.printing.preview(string, viewer="file", filename="test.png")
