import os
import re
import requests
import urllib.parse
from datetime import datetime
from flask import redirect, render_template, request, session
from functools import wraps


def apology(message,path):
    return render_template("apology.html", message = message, value = path)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            print("here")
            return redirect("/")
        print("there")
        return f(*args, **kwargs)
    return decorated_function


def Isstaff(db,user_id):
    user = db.execute('SELECT user_id FROM staff')
    out = [value["user_id"] for value in user]
    if user_id in out:
        return True
    return False

def month_num(month):
     month_val = str(datetime.strptime(month,'%B').month)
     return month_val

def validate_password(password):
    string_check= re.compile('[@_!#$%^&*]')
    dig_check = len([x for x in password if x.isdigit()])
    if len(password)<8:
        return ("The password should be atleast 8 characters wide")
    if not password[0].isalpha():
        return ("The password's first character must be a letter")
    if not any([(x.isupper() for x in password)]):
        return ("The password must contain atleast one capital letter")
    if password.isalpha():
        return ("The string doesn't contain atleast a single digit")
    if not bool(string_check.search(password)):
        return ("The string doesn't contain a special character")