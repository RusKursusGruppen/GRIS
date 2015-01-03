# -*- coding: utf-8 -*-

from gris import db
Model = db.Model
Table = db.Table

Column = db.Column
Integer = db.Integer
Text = db.Text # Use this instead of strings
Boolean = db.Boolean
Date = db.Date
ForeignKey = db.ForeignKey
relationship = db.relationship
backref = db.backref

### USERS ###
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

    # def __init__(self, username, raw_password, name, email, groups=[]):
    #     """Create a new user."""
    #     self.username = username
    #     self.password = raw_password # TODO: fix!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1
    #     self.name = name
    #     self.email = email

    #     added_groups = []
    #     for group in groups:
    #         if isinstance(group, Group):
    #             self.groups.append(group)
    #         else:
    #             groupname = group
    #             group = Group.query.filter_by(groupname=groupname).first()
    #             if group is None:
    #                 group = Group(groupname)
    #                 added_groups.append(group)

class Group(Model):
    id = Column(Integer, primary_key=True)
    groupname = Column(Text, unique=True, nullable=False)
    def __init__(self, groupname):
        self.groupname = groupname

users_groups = Table("users_groups",
                     Column("user_id", Integer, ForeignKey("user.id")),
                     Column("group_id", Integer, ForeignKey("group.id")))
User.groups = relationship("Group", secondary=users_groups, backref="users")