from __future__ import division
from app import app
from app.models import DEBT, PAYMENT, CLEAR_ALL
from flask import jsonify, request
from flask.ext.login import current_user
from app.extras import login_required
from app.services import db as dbsrv
# from app import db
# routes for manipulating the database

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
        return jsonify({"message":"No such user(s).", "result":1})

    # verify that the group exists
    group = dbsrv.group_exists(group_id)
    if not group:
        return jsonify({"message":"No such group.", "result":2})

    #determine kind
    if kind == "debt":
        kindn = DEBT
    if kind == "payment":
        kindn = PAYMENT

    # verify that all users are members of the group
    if not dbsrv.users_in_group(to_user + from_users, group):
        # if not, return the error
        return jsonify({"message":"Users are not in the requested group.",
                        "result": 3})
    else:
        # if so, add the requested transactions
        for from_id in from_ids:
            dbsrv.add_transaction(group_id, from_id, to_id[0],
                                amount/len(from_ids), kindn)
        return jsonify({"result":0,"message":"success"})

@app.route('/clearall/<int:group_id>',methods=['POST'])
@login_required
def clearall(group_id, dbsrv = dbsrv):
    # verify that this group_id exists
    group = dbsrv.group_exists(group_id)
    if not group:
        return jsonify({"message":"No such group.",
                        "result":2})

    # verify that the current user is an admin for this group_id
    if not dbsrv.user_is_admin(current_user,group):
        return jsonify({"message":"Not authorized",
                        "result":4})

    #if we are here, add the transaction
    dbsrv.add_transaction(int(group_id),0,0,0,CLEAR_ALL)
    return jsonify({"message":"success",
                    "result":0})

@app.route('/addadmin',methods=["POST","GET"])
@login_required
def addadmin(dbsrv = dbsrv):
    # verify that user, group, and membership exist
    args = request.get_json()
    group_id = args['group']
    user_ids = args['user']

    group = dbsrv.group_exists(group_id)
    if not group:
        return jsonify({"message":"No such group.",
                        "result":2})

    users = dbsrv.users_exist(user_ids)
    if not users:
        return jsonify({"message":"No such user.",
                            "result":1})
    else:
        if not dbsrv.users_in_group(users,group):
            return jsonify({"message":"User is not in the requested group.",
                            "result":3})
        # return error if user is already an admin
        if any([dbsrv.user_is_admin(user,group) for user in users]):
            return jsonify({"message":"User is already an admin.",
                            "result":5})
        # if all errors clear, make the users admins
        dbsrv.set_admins(users,group,True)

    # return
    return jsonify({"result":0,"message":"success"})

@app.route('/resign/<int:group_id>', methods=["POST"])
@login_required
def resign(group_id,dbsrv=dbsrv):
    # make sure group exists and user is a member of it
    group = dbsrv.group_exists(group_id)
    if not group:
        return jsonify({"message":"No such group.",
                        "result":2})
    if not dbsrv.users_in_group([current_user],group):
        return jsonify({"message":"User is not in the requrested group.",
                        "result":3})

    # make sure user is an admin in the group
    if dbsrv.user_is_admin(current_user,group) == False:
        return jsonify({"message":"You are not an admin in this group.",
                        "result":6})

    # if everything looks good, set admin to False
    dbsrv.set_admins([current_user],group,False)
    return jsonify({"result":0,"message":"success"})
