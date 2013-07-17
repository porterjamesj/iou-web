from __future__ import division
from app import app
from app.models import DEBT, PAYMENT, CLEAR_ALL
from flask import jsonify, request
from flask.ext.login import current_user
from app.extras import login_required
from app.services import db as dbsrv

# dict of possible responses

responses = {"success": {"result":0,"message":"success"},
             "nouser": {"message":"No such user(s).", "result":1},
             "nogroup": {"message":"No such group.", "result":2},
             "not_members": {"message": "Users are not in the requested group.",
                             "result": 3},
            "notauth": {"message":"Not authorized", "result":4},
            "admin_already": {"message":"User is already an admin.", "result":5},
            "member_already": {"message":"User is already a member.", "result":6}
            }

@app.route('/add',methods=['POST'])
@login_required
def addtrans(dbsrv = dbsrv):
    # extract info from requests
    args = request.get_json()
    group_id = args['group_id']
    from_ids = args['from']
    to_id = args['to_id'] # allow this to be an int?
    amount = args['amount']
    kind = args['kind']

    # verify that all users exist
    from_users = dbsrv.users_exist(from_ids)
    to_user = dbsrv.users_exist(to_id)

    if not from_users or not to_user:
        return jsonify(responses["nouser"])

    # verify that the group exists
    group = dbsrv.group_exists(group_id)
    if not group:
        return jsonify(responses["nogroup"])

    #determine kind
    if kind == "debt":
        kindn = DEBT
    if kind == "payment":
        kindn = PAYMENT

    # verify that all users are members of the group
    if not dbsrv.users_in_group(to_user + from_users, group):
        # if not, return the error
        return jsonify(responses["not_members"])
    else:
        # if so, add the requested transactions
        for from_id in from_ids:
            dbsrv.add_transaction(group_id, from_id, to_id[0],
                                amount/len(from_ids), kindn)
        return jsonify(responses["success"])

@app.route('/clearall/<int:group_id>',methods=['POST'])
@login_required
def clearall(group_id, dbsrv = dbsrv):
    # verify that this group_id exists
    group = dbsrv.group_exists(group_id)
    if not group:
        return jsonify(responses["nogroup"])

    # verify that the current user is an admin for this group_id
    if not dbsrv.user_is_admin(current_user,group):
        return jsonify(responses["notauth"])

    #if we are here, add the transaction
    dbsrv.add_transaction(int(group_id),0,0,0,CLEAR_ALL)
    return jsonify(responses["success"])

@app.route('/addadmin',methods=["POST","GET"])
@login_required
def addadmin(dbsrv = dbsrv):
    # verify that user, group, and membership exist
    args = request.get_json()
    group_id = args['group']
    user_ids = args['user']

    group = dbsrv.group_exists(group_id)
    if not group:
        return jsonify(responses["nogroup"])

    users = dbsrv.users_exist(user_ids)
    if not users:
        return jsonify(responses["nouser"])
    else:
        if not dbsrv.users_in_group(users,group):
            return jsonify(responses["not_member"])
        # return error if user is already an admin
        if any([dbsrv.user_is_admin(user,group) for user in users]):
            return jsonify(responses["admin_already"])
        # if all errors clear, make the users admins
        dbsrv.set_admins(users,group,True)

    # return
    return jsonify(responses["success"])

@app.route('/resign/<int:group_id>', methods=["POST"])
@login_required
def resign(group_id,dbsrv=dbsrv):
    # make sure group exists and user is a member of it
    group = dbsrv.group_exists(group_id)
    if not group:
        return jsonify(responses["nogroup"])
    if not dbsrv.users_in_group([current_user],group):
        return jsonify(responses["not_members"])

    # make sure user is an admin in the group
    if dbsrv.user_is_admin(current_user,group) == False:
        return jsonify(responses["notauth"])

    # if everything looks good, set admin to False
    dbsrv.set_admins([current_user],group,False)
    return jsonify(responses["success"])


@app.route('/search/users/<querystring>',methods=["POST"])
@login_required
def search_users(querystring,dbsrv = dbsrv):
    users = dbsrv.search_users(querystring)
    userlist = []
    for user in users:
        userdict = {"id":user.id,
                    "name":user.name,
                    "email":user.email,
                    "groups": [g.id for g in user.groups]}
        userlist.append(userdict)
    return jsonify({"users":userlist})

@app.route('/search/groups/<querystring>',methods=["POST"])
@login_required
def search_groups(querystring, dbsrv = dbsrv):
    groups = dbsrv.search_groups(querystring)
    grouplist = []
    for group in groups:
        groupdict = {"id":group.id,
                     "name":group.name,
                     "members": [m.email for m in group.members]}
        grouplist.append(groupdict)
    return jsonify({"groups":grouplist})

@app.route('/addmember',methods=["POST"])
@login_required
def add_member(dbsrv=dbsrv):
    args = request.get_json()
    group_id = args['group_id']
    user_id = args['user_id']

    # check that user and group exist
    user = dbsrv.users_exist([user_id])
    group = dbsrv.group_exists(group_id)
    if not user:
        return jsonify(responses["nouser"])

    if not group:
        return jsonify(responses["nogroup"])

    dbsrv.add_member(user,group)
    return jsonify(responses["success"])
