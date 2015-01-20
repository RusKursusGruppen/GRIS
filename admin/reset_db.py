# -*- coding: utf-8 -*-

from gris import app, data

def reset_db():
    data.execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public")
    data.script("schema.sql")

if __name__ == "__main__":
    with app.app_context():
        reset_db()
