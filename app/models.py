from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    """Keeps track of basic information about a user."""
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(60))
    email = db.Column(db.String(100))
    dummy = db.Column(db.Boolean)
    pw_hash = db.Column(db.String(160))

    # pw hashing and checking
    def set_password(self, password):
        self.pw_hash = generate_password_hash(password)

    def check_password(self,password):
        return check_password_hash(self.pw_hash, password)

    #methods required by flask-login
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return not self.dummy

    def get_id(self):
        return unicode(self.id)

    # other
    def __repr__(self):
        return "<User {0}>".format(self.name)


class Group(db.Model):
    """Manages facts about groups. Name, etc."""
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(60))

    def __repr__(self):
        return "<Group {0}>".format(self.name)


class Member(db.Model):
    """Keeps track of which users are
    members of which groups, and whether or not members of groups
    are admins."""
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    admin = db.Column(db.Boolean)

class Trans(db.Model):
    """A table of all transactions, which are either debts or
    credits, although this is not explicitly represented, it
    is implicit in whether the value is positive or negative"""
    id = db.Column(db.Integer, primary_key = True)
    from_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    to_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    amount = db.Column(db.Numeric(precision = 2))
    fresh = db.Column(db.Boolean)
