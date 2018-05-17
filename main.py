# -*- coding: utf-8 -*-
from importlib import import_module
from flask import Flask, request, render_template

from config import *


app = Flask(__name__)

def examinate_func(f):
    failed = []
    for params, output in TESTCASE:
        result = f(**params)
        if not (len(result) == len(output) and all([result[i] == o for i, o in enumerate(output)])):
            failed.append([params, output, result])
    return failed


@app.route("/pycourse/assignment8", methods=["GET", "POST"])
def examinate_assignment8():
    if request.method == "GET":
        return render_template('assignment8.html')
    else:
        name = request.form["name"]
        upload_file = request.files['assignment']
        upload_file.save(ASSIGNMENT_DIR)

        assignment = import_module(upload_file.filename, package="assignment8")
        func = getattr(assignment, FUNCTION_NAME)
        if func:
            failed = examinate_func(func)
            if failed:
                pass
            else:
                pass
        else:
            pass


if __name__ == '__main__':
    app.run(debug=True)