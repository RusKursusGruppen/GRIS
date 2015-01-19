# -*- coding: utf-8 -*-

from flask import Blueprint, request, session

from lib.tools import abort, jsonify, logged_in, now, success

blueprint = Blueprint("news", __name__, url_prefix="/api")
from gris import data


@blueprint.route('/news')
@logged_in
def news():
    news = data.execute("SELECT * FROM News ORDER BY created DESC")
    return jsonify(news)

@blueprint.route('/news/new', methods=["POST"])
@logged_in
def new():
    b = data.Bucket(request.form)
    b.creator = session['user_id']
    b.created = now()
    if b.title == "":
        abort(400, "illegal title")
    b.body
    b >= "News"
    return success()

@blueprint.route('/news/update', methods=["POST"])
@logged_in
def update():
    b = data.Bucket(request.form)
    news = data.execute("SELECT * FROM News WHERE news_id = ?", b["news_id"]).one()
    b.last_updated = now()
    if session["user_id"] != news["creator"] or not is_admin():
        abort(403, "You are not the creator")

    if "title" in b:
        if b.title == "":
            abort(400, "illegal title")

    if "body" in b:
        b.body

    b >> ("UPDATE News $ WHERE news_id = ?", b["news_id"])
    return success()

@blueprint.route('/news/delete', methods=["POST"])
@logged_in
def delete():
    b = data.Bucket(request.form)
    news = data.execute("SELECT * FROM News WHERE news_id = ?", b["news_id"]).one()
    if session["user_id"] != news["creator"] or not is_admin():
        abort(403, "You are not the creator")
    with data.transaction() as t:
        t.execute("DELETE FROM News WHERE news_id = ?", b.news_id)
        t.execute("DELETE FROM News_access where news_id = ?", b.news_id)
    return success()
