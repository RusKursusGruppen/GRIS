
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, get_flashed_messages, escape, Blueprint


from lib import data, password, mail
from lib.tools import logged_in, empty, url_front
import config
import datetime, string, time, subprocess

admin = Blueprint('admin', __name__, template_folder = '../templates/admin')

@admin.route('/admin', methods=['GET', 'POST'])
def overview():
    #adminrights
    return render_template("admin/admin.html")

@admin.route('/admin/git_pull', methods=["GET", "POST"])
def git_pull():
    if request.method == "POST":
        response = subprocess.check_output(["git", "pull"])
        response = response.replace("\n", "<br />")
    else:
        response = ""
    return render_template("admin/git_pull.html",response=response)
