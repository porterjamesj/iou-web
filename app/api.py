from app import app, login_manager, db
from models import User, Member, Group, Trans
from flask import jsonify, request
from flask.ext.login import login_required
import services as srv

# routes for manipulating the database

@app.route('/add',methods=['POST'])
@login_required
def addtrans():
    # extract info from requests
    group_id = request.args.get('group_id')
    from_id = request.args.get('from_id')
    to_id = request.args.get('to_id')
    amount = request.args.get('amount')

    fromuser = User.query.get(from_id)
    touser = User.query.get(to_id)

    # verify that both users exist
    if fromuser == None or touser == None:
        return jsonify({"errmsg":"No such user(s).",
                        "errcode":0})

    group = Group.query.get(group_id)
    # verify that the group exists
    if group == None:
        return jsonify({"errmsg":"No such group.",
                        "errcode":1})

    # verify that both users are members of the group
    if fromuser in group.members and touser in group.members:
        srv.add_transaction(group_id, from_id, to_id, amount)
        return jsonify(result = "success")
    else:
        return jsonify({"errmsg":"Users are not in the requested group.",
                        "errcode": 2})
