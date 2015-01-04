# -*- coding: utf-8 -*-

from gris import db
Model = db.Model
Table = db.Table
Column = db.Column
ForeignKey = db.ForeignKey
relationship = db.relationship
backref = db.backref

Boolean = db.Boolean
Date = db.Date
DateTime = db.DateTime
Integer = db.Integer
Text = db.Text # Use this instead of strings

### USERS ###
class User(Model):
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

class Group(Model):
    id = Column(Integer, primary_key=True)
    groupname = Column(Text, unique=True, nullable=False)
    def __init__(self, groupname):
        self.groupname = groupname

users_groups = Table("users_groups",
                     Column("user_id", Integer, ForeignKey("user.id")),
                     Column("group_id", Integer, ForeignKey("group.id")))
User.groups = relationship("Group", secondary=users_groups, backref="users")

class User_creation_key(Model):
    key = Column(Text, primary_key=True)
    email = Column(Text, nullable=False)
    created = Column(DateTime, nullable=False, default=db.func.now())

class User_forgotten_password_key(Model):
    key = Column(Text, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    created = Column(DateTime, nullable=False, default=db.func.now())
