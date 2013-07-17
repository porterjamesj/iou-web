from app.models import Trans, User, Member, Group, CLEAR_ALL
from app import db
from time import time

def add_transaction(group_id, from_id, to_id, amount, kind):
    """Add the specified transaction to the database."""
    newtrans = Trans(group_id = group_id,
                     from_id = from_id,
                     to_id = to_id,
                     amount = amount,
                     time = time(),
                     kind = kind)
    db.session.add(newtrans)
    db.session.commit()

def users_exist(user_ids):
    """Given a list of user ids, return a list of them if they do exist,
    otherwise return false."""
    users = User.query.filter(User.id.in_(user_ids)).all()
    if len(users) != len(user_ids):
        return False
    else:
        return users

def group_exists(group_id):
    """Return the group if it exists, otherwise return False."""
    group = Group.query.get(group_id)
    if group == None:
        return False
    else:
        return group

def users_in_group(users,group):
    """Return true if all users are members of the group, false
    otherwise."""
    if all([user in group.members for user in users]):
        return True
    else:
        return False

def user_is_admin(user,group):
    """Return true if the user is an admin for the group, false
    otherwise."""
    admins = Member.query.filter(Member.admin == True,
                                 Member.group_id == group.id).all()
    if user.id in [admin.user_id for admin in admins]:
        return True
    else:
        return False

def set_admins(users,group,setting):
    """Set the admin status of the user with user_id in the group
    group_id to the requested setting."""
    members = Member.query.filter(Member.user_id.in_([u.id for u in users]),
                                  Member.group_id == group.id)
    for member in members:
        member.admin = setting
    db.session.commit()

def search_users(querystring):
    """Return all the users whose name or email is like the query string."""
    foundname = User.query.filter(User.name.like("%" + querystring + "%")).all()
    foundemail = User.query.filter(User.email.like("%" + querystring + "%")).all()
    return set(foundname+foundemail)

def search_groups(querystring):
    """Return all groups whose name is like the query string."""
    return set(Group.query.filter(Group.name.like("%" + querystring + "%")).all())
