# -*- coding: utf-8 -*-

from gris import db
Model = db.Model
Column = db.Column
Integer = db.Integer
Text = db.Text # Use this instead of strings
Boolean = db.Boolean
Date = db.Date

class User(db.Model):
    id = Column(Integer, primary_key=True)
    username = Column(Text, unique=True, nullable=False)
    password = Column(Text, nullable=False)

    name = Column(Text, default="RUS")
    driverslicence = Column(Boolean, default=False)
    address = Column(Text)
    zipcode = Column(Text)
    city = Column(Text)
    phone = Column(Text)
    email = Column(Text)
    birthday = Column(Date)

    diku_age = Column(Text) # TODO: Should this be text? or should we have a nullable reference to the rus instance of this user?
    about_me = Column(Text)

    deleted = Column(Boolean, default=False) # Field for marking a user as deleted
