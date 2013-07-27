"""API routes."""
from __future__ import division
from app import app
from app.models import DEBT, PAYMENT, CLEAR_ALL
from flask import jsonify, request
from flask.ext.login import current_user, login_required
from app.services import db as dbsrv
from app import errors as err

# the success respones
success = {"result": 0, "message": "success"}


# TRANS


@app.route('/transactions', methods=['POST'])
# @login_required
def posttrans(dbsrv=dbsrv):
    # try to extract info from JSON
    try:
        args = request.get_json()
        kind = args.get('kind')
        group_id = args.get('group_id')
        # these params won't be present if its a clear
        from_ids = args.get('from_ids')
        to_id = args.get('to_id')
        amount = args.get('amount')

        #determine kind
        if kind == "debt":
            kindn = DEBT
        elif kind == "payment":
            kindn = PAYMENT
        elif kind == "clear":
            kindn = CLEAR_ALL
        else:
            raise RuntimeError("Transaction type not specified correctly.")
    except:
        raise err.JSONParseError("JSON Parsing Failed.")

    # if this is a debt or a payment, try to add the transactions
    if kindn in [DEBT, PAYMENT]:
        for from_id in from_ids:
            print from_id
            dbsrv.add_transaction(group_id, from_id, to_id,
                                  amount/len(from_ids), kindn)
    elif kindn == CLEAR_ALL:
        dbsrv.clear_all(group_id)
    return jsonify(success)


# USER


@app.route('/users', methods=["GET"])
# @login_required
def search_users(dbsrv=dbsrv):
    """A GET request to /users will do a search."""
    try:
        args = request.get_json()
        query = args['query']
    except:
        raise err.JSONParseError("JSON Parsing failed.")
    users = dbsrv.search_users(query)
    userlist = []
    for user in users:
        userdict = {"id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "groups": [g.id for g in user.groups]}
        userlist.append(userdict)
    return jsonify({"result": userlist})


@app.route('/users/<int:user_id>', methods=["PUT"])
# @login_required
def putuser(user_id, dbsrv=dbsrv):
    """A PUT request to users will update some combination of
    name, email, and admin status."""
    try:
        args = request.get_json()
        name = args.get('name')
        email = args.get('email')
        admin = args.get('admin')
        # this is only needed if we are changing admin status
        group_id = args.get('group_id')
    except:
        raise err.JSONParseError("JSON Parsing Failed.")
    if name is not None or email is not None:
        dbsrv.change_user(user_id,
                          name=name,
                          email=email)
    if admin is not None and group_id is not None:
        print type(admin)
        dbsrv.set_admin(user_id, group_id, bool(admin))
    # return
    return "", 200


@app.route('/users/<int:user_id>', methods=["GET"])
# @login_required
def getuser(user_id, dbsrv=dbsrv):
    """This will get a specific user_id."""
    user = dbsrv.get_user(user_id)
    if not user:
        return "", 404
    else:
        return jsonify({"users": {"name": user.name,
                                  "email": user.email,
                                  "groups": [g.id for g in user.groups]}})

# GROUP


@app.route('/groups', methods=["GET"])
# @login_required
def search_groups(dbsrv=dbsrv):
    """A GET request to /groups does a search."""
    try:
        args = request.get_json()
        query = args['query']
    except:
        raise err.JSONParseError("JSON Parsing failed.")
    groups = dbsrv.search_groups(query)
    grouplist = []
    for group in groups:
        groupdict = {"id": group.id,
                     "name": group.name,
                     "members": [m.id for m in group.members]}
        grouplist.append(groupdict)
    return jsonify({"groups": grouplist})


@app.route('/groups/<int:group_id>/users/<int:user_id>', methods=['GET'])
# @login_required
def is_member(group_id, user_id):
    if dbsrv.users_in_group(user_id, group_id):
        return "", 200
    else:
        return "", 404


@app.route('/groups/<int:group_id>/users/<int:user_id>', methods=['POST'])
# @login_required
def new_member(group_id, user_id):
    """A PUT of this format will make a user a member of a group."""
    dbsrv.add_member(user_id, group_id)
    return "", 200


@app.route('/groups/<int:group_id>', methods=["GET"])
def get_group(group_id):
    """Get info on a specific group."""
    group = dbsrv.get_group(group_id)
    if not group:
        return "", 404
    else:
        return jsonify({"groups": {"name": group.name,
                                   "members": [u.id for u in group.members]}})


@app.route('/groups/<int:group_id>', methods=["PUT"])
def put_group(group_id):
    try:
        args = request.get_json()
        name = args["name"]
    except:
        err.JSONParseError("JSON Parsing failed.")
    dbsrv.set_name(group_id, name)
    return "", 200


#SELF


@app.route('/self', methods=["PUT"])
# @login_required
def putself(group_id, dbsrv=dbsrv):
    try:
        args = request.get_json()
        group_id = args.get('group_id')
        action = args.get('action')
    except:
        raise err.JSONParseError("JSON Parsing Failed.")
    if action == "resign":
        dbsrv.set_admin(current_user, group_id, False)
    return jsonify(success)
