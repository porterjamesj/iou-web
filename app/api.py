from __future__ import division
from app import app
from app.models import User, Member, Group, Trans, DEBT, PAYMENT, CLEAR_ALL
from flask import jsonify, request
from flask.ext.login import login_required,current_user
import app.services as srv

# routes for manipulating the database

@app.route('/add',methods=['POST'])
@login_required
def addtrans():
    # extract info from requests
    args = request.get_json()
    group_id = args['group_id']
    from_ids = args['from']
    to_id = args['to_id']
    amount = args['amount']
    kind = args['kind']

    fromusers = User.query.filter(User.id.in_(from_ids)).all()
    touser = User.query.get(to_id)

    # verify that all users exist
    if touser == None or None in fromusers:
        return jsonify({"message":"No such user(s).",
                        "result":1})

    group = Group.query.get(group_id)
    # verify that the group exists
    if group == None:
        return jsonify({"message":"No such group.",
                        "result":2})

    #determine kind
    if kind == "debt":
        kindn = DEBT
    if kind == "payment":
        kindn = PAYMENT

    # verify that both users are members of the group
    if touser in group.members and all([fromuser in group.members
                                      for fromuser in fromusers]):
        # if so, add the requested transactions
        for from_id in from_ids:
            srv.add_transaction(group_id, from_id, to_id,
                                amount/len(from_ids), kindn)
        return jsonify({"result":0,"message":"success"})
    else:
        return jsonify({"message":"Users are not in the requested group.",
                        "result": 3})

@app.route('/clearall/<int:group_id>',methods=['POST'])
@login_required
def clearall(group_id):
    # verify that this group_id exists
    group = Group.query.get(group_id)
    if group == None:
        return jsonify({"message":"No such group.",
                        "result":2})

    # verify that the current user is an admin for this group_id
    if current_user.id not in [user.id for user in group.members]:
        return jsonify({"message":"Not authorized",
                        "result":4})

    #if we are here, add the transaction
    srv.add_transaction(int(group_id),0,0,0,CLEAR_ALL)
    return jsonify({"message":"success",
                    "result":0})
