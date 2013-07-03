from app import db
from werkzeug.security import generate_password_hash, check_password_hash

ROLE_USER = 0
ROLE_ADMIN = 1

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(100))
    role = db.Column(db.SmallInteger, default = ROLE_USER)
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
        return False

    def get_id(self):
        return unicode(self.id)

    # other

    def __repr__(self):
        return "<User {0}>".format(self.name)
