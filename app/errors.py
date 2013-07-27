from app import app
from flask import jsonify
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from app import db


class APIError(Exception):
    pass


class JSONParseError(APIError):
    pass


class AuthorizationError(APIError):
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


@app.errorhandler(IntegrityError)
def integrity_error(error):
    # need to manually rollback the session when this happens
    db.session.rollback()
    response = jsonify({"message":
                        "Database integrity violation. "
                        "Verify that the ids you are "
                        "using actually exist."})
    response.status_code = 404


@app.errorhandler(AuthorizationError)
def auth_error(error):
    response = jsonify({"message":
                        "Authorization error. You are not "
                        "authenticated as an admin in the group "
                        "you are attempting to query or modify. "})
    response.status_code = 401


@app.errorhandler(DatabaseError)
@app.errorhandler(NoResultFound)
@app.errorhandler(MultipleResultsFound)
def database_error(error):
    response = jsonify({"message":
                        "Database error. Please verify that the data you "
                        "are trying to insert is sensible. "})
    response.status_code = 404
    return response


@app.errorhandler(JSONParseError)
def json_parse_error(error):
    response = jsonify({"message":
                        "JSON parsing failed."})
    response.status_code = 404
    return response
