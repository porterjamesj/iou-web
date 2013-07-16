from __future__ import division
from app import app
from app.models import User, Member, Group, Trans, DEBT, PAYMENT, CLEAR_ALL
from flask import jsonify, request
from flask.ext.login import login_required,current_user
import app.services as srv
from app import db #probably should have enough services so that this is unnecessary
# routes for manipulating the database

@app.route('/add',methods=['POST'])
@login_required
def addtrans():
    # extract info from requests
    args = request.get_json()
    group_id = args['group_id']
    from_ids = args['from']
    to_id = args['to_id'][0] # should allow this to be a literal
    amount = args['amount']
    kind = args['kind']

    fromusers = User.query.filter(User.id.in_(from_ids)).all()
    touser = User.query.get(to_id)

    # verify that all users exist
    if touser == None or None in fromusers:
        return jsonify({"message":"No such user(s).",
                        "result":1})

    # verify that the group exists
    group = Group.query.get(group_id)
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

@app.route('/addadmin',methods=["POST","GET"])
@login_required
def addadmin():
    # verify that user, group, and membership exist
    args = request.get_json()
    group_id = args['group']
    user_ids = args['user']
    group = Group.query.get(group_id)

    if group == None:
        return jsonify({"message":"No such group.",
                        "result":2})
    for user_id in user_ids:
        user = User.query.get(user_id)
        if user == None:
            return jsonify({"message":"No such user.",
                            "result":1})
        if user not in group.members:
            return jsonify({"message":"User is not in the requrested group.",
                            "result":3})
        # get the membership
        member = Member.query.filter(Member.user_id == user_id,
                                     Member.group_id == group_id).one()
        # throw an error if the user is already an admin
        if member.admin == True:
            return jsonify({"message":"User is already an admin.",
                            "result":5})
        # if all errors clear, make the user an admin
        member.admin = True

    # commit and return
    db.session.commit()
    return jsonify({"result":0,"message":"success"})

@app.route('/resign/<int:group_id>')
@login_required
def resign(group_id):
    group = Group.query.get(group_id)

    # make sure group exists and user is a member of it
    if group == None:
        return jsonify({"message":"No such group.",
                        "result":2})
    if current_user not in group.members:
        return jsonify({"message":"User is not in the requrested group.",
                        "result":3})

    # make sure user is an admin in the group
    member = Member.query.filter(Member.user_id == current_user.id,
                                 Member.group_id == group_id).one()

    if member.admin == False:
        return jsonify({"message":"You are not an admin in this group.",
                        "result":6})

    # if everything looks good, set admin to False
    member.admin = False
    db.session.commit()
    return jsonify({"result":0,"message":"success"})
