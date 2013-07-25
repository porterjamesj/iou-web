from app import app
from flask import jsonify
from sqlalchemy.exc import IntegrityError
from app import db


class AuthorizationError(Exception):
    pass


class DatabaseError(Exception):
    pass


class UserNotFoundError(DatabaseError):
    pass


class GroupNotFoundError(DatabaseError):
    pass


class UsersNotInGroupError(DatabaseError):
    pass


class SetAdminError(DatabaseError):
    pass


class MemberAlreadyError(DatabaseError):
    pass


# flask errorhandlers

@app.errorhandler(AuthorizationError)
def auth_error(error):
    return jsonify({"message":
                    """Authorization error. You are not
                    authenticated as an admin in the group
                    you are attempting to query or modify.""",
                    "result": 3})


@app.errorhandler(DatabaseError)
def database_error(error):
    return jsonify({"message":
                    """Database error. Please verify that the data you
                    are trying to insert is sensible.""",
                    "result": 2})


@app.errorhandler(IntegrityError)
def integrity_error(error):
    # need to manually rollback the session when this happens
    db.session.rollback()
    return jsonify({"message":
                    """Database integrity violation.
                    Verify that the ids you are
                    using actually exist.""",
                    "result": 1})
