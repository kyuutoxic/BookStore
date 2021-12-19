from flask import render_template, redirect, request
from __init__ import app, login
from admin import *
from models import *
from flask_login import login_user, logout_user
import utils


@app.route('/admin-login', methods=['post'])
def admin_login():
    username = request.form['username']
    password = request.form['password']

    user = utils.check_login(username=username,
                            password=password)
    if user:
        login_user(user=user)

    return redirect('/admin')


@login.user_loader
def user_load(user_id):
    return utils.get_user_by_id(user_id=user_id)


if __name__ == '__main__':
    app.run(debug=True)