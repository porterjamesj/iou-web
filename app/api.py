from app import app, login_manager, db
from models import User, Member, Group, Trans
from flask import jsonify, request
from flask.ext.login import login_required

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

    # verify that the group exists
    if Group.query.get(group_id) == None:
        return jsonify({"errmsg":"No such group.",
                        "errcode":1})

    # verify that both users are members of the group
    try:
        Member.query.filter(Member.group_id == group_id)\
          .filter(Member.user_id == from_id).one()
        Member.query.filter(Member.group_id == group_id)\
          .filter(Member.user_id == to_id).one()

    except:
        return jsonify({"errmsg":"Users are not in the requested group.",
                        "errcode": 2})

    # we are good to add the transaction
    newtrans = Trans(group_id = group_id,
                     from_id = from_id,
                     to_id = to_id,
                     amount = amount,
                     fresh = True)
    db.session.add(newtrans)
    db.session.commit()
    return jsonify(result = "success")
