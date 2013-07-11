from __future__ import division
from app import app
from app.models import User, Member, Group, Trans, DEBT, PAYMENT
from flask import jsonify, request
from flask.ext.login import login_required
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

    fromusers = [User.query.get(from_id) for from_id in from_ids]
    touser = User.query.get(to_id)

    # verify that all users exist
    if touser == None or None in fromusers:
        return jsonify({"errmsg":"No such user(s).",
                        "errcode":0})

    group = Group.query.get(group_id)
    # verify that the group exists
    if group == None:
        return jsonify({"errmsg":"No such group.",
                        "errcode":1})

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
        return jsonify(result = "success")
    else:
        return jsonify({"errmsg":"Users are not in the requested group.",
                        "errcode": 2})
