# -*- coding: utf-8 -*-
import os
from importlib import import_module
from flask import Flask, request, render_template

from config import *


app = Flask(__name__, static_url_path="/pycourse/static")

def examinate_func(f, test_cases):
    errors = []
    for params, expected in test_cases:
        result = f(**params)
        if isinstance(result, tuple):
            if not (len(result) == len(expected) and all([result[i] == o for i, o in enumerate(expected)])):
                errors.append((params, expected, result))
        else:
            if not result == expected[0]:
                errors.append((params, expected, (result, )))
    return {"status": WRONG_RETURN, "errors": errors} if errors else {"status": PASSED}


def check_func(f, checker):
    errors = []
    check_f = checker["func"]
    for params in checker["cases"]:
        code, msg = check_f(f, **params)
        if code == CHECK_FAILED:
            errors.append((params, msg))
    return {"status": CHECK_FAILED, "errors": errors} if errors else {"status": PASSED}


def format_func_call(func_name, params):
    param_s = ", ".join(["{}={}".format(k, v) for k, v in params.items()])
    return "{}({})".format(func_name, param_s)


def format_error(func_name, error_info):
    status = error_info["status"]
    if status == WRONG_RETURN:
        formated_errors = []
        for params, expected, result in error_info["errors"]:
            func_call = format_func_call(func_name, params)
            expected_s = ", ".join((str(e) for e in expected))
            result_s = ", ".join((str(r) for r in result))
            formated_errors.append((func_call, expected_s, result_s))
        error_info["errors"] = formated_errors
    elif status == CHECK_FAILED:
        formated_errors = []
        for params, msg in error_info["errors"]:
            func_call = format_func_call(func_name, params)
            formated_errors.append((func_call, msg))
        error_info["errors"] = formated_errors


@app.route("/pycourse/assignment8", methods=["GET", "POST"])
def examinate_assignment8():
    if request.method == "GET":
        return render_template('assignment8.html')
    else:
        name = request.form["name"]
        upload_file = request.files['assignment']
        filename = upload_file.filename
        upload_file.save(os.path.join(ASSIGNMENT_DIR, filename))
        assignment = import_module("assignment8.{}".format(filename).replace(".py", ""))

        passed = True
        result = []
        for func_name in FUNCTION_NAMES:
            func = getattr(assignment, func_name)
            if func:
                if func_name in TESTCASE:
                    info = examinate_func(func, TESTCASE[func_name])
                else:
                    info = check_func(func, CHECKERS[func_name])

                if info["status"] != PASSED:
                    format_error(func_name, info)
                    passed = False
                result.append(info)
            else:
                result.append({"status": NOT_FOUND})
        return render_template("result.html", name=name, result=result, passed=passed, enumerate=enumerate,
                               status=STATUS)


if __name__ == '__main__':
    app.run(debug=True)