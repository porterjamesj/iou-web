from app.models import Trans, User, Member, Group, CLEAR_ALL
from app import db
from time import time
import app.errors as err


# TRANSACTION


def add_transaction(group_id, from_id, to_id, amount, kind):
    """Add the specified transaction to the database."""
    # check that that the users are members of the group

    if not users_in_group([from_id, to_id], group_id):
        raise err.UsersNotInGroupError("Users not in requested group .")
    # now add the transaction
    newtrans = Trans(group_id=group_id,
                     from_id=from_id,
                     to_id=to_id,
                     amount=amount,
                     time=time(),
                     kind=kind)
    db.session.add(newtrans)
    db.session.commit()


def clear_all(group_id):
    if not get_group(group_id):
        raise err.GroupDoesNotExistError
    clear = Trans(group_id=group_id,
                  kind=CLEAR_ALL,
                  time=time())
    db.session.add(clear)
    db.session.commit()


# USER


def change_user(user_id, name=None, email=None):
    """Change the user's name and email to the given parameters,
    if they are passed."""
    user = User.query.get(user_id)
    if not user:
        raise err.UserDoesNotExistError
    if name:
        user.name = name
    if email:
        user.email = email
    db.session.commit()


def get_user(user_id):
    """Return a speciic user from the database."""
    return User.query.get(user_id)


def search_users(querystring):
    """Return all the users whose name or email is like the query string."""
    foundname = User.query.filter(
        User.name.like("%" + querystring + "%")).all()
    foundemail = User.query.filter(
        User.email.like("%" + querystring + "%")).all()
    return set(foundname+foundemail)


# MEMBER


def users_in_group(user_ids, group_id):
    """Return true if all users are members of the group, false
    otherwise. Accepts either a single integer user_id of a list of
    same. Will return False rather than throw an error if the user
    or the group does not exist, perhaps this should be changed"""
    if type(user_ids) is int:
        user_ids = [user_ids]

    members = Member.query.filter(Member.group_id == group_id,
                                  Member.user_id.in_(user_ids)).all()
    if len(members) == len(user_ids):
        return True
    else:  # someone is not in the group
        return False


def add_member(user_id, group_id):
    """Make the user a member of the group, but not an admin."""
    if users_in_group([user_id], group_id):
        raise err.MemberAlreadyError(
            "User is already a member of this group.")
    else:
        member = Member(user_id=user_id,
                        group_id=group_id,
                        admin=False)
        db.session.add(member)
        db.session.commit()


def set_admin(user_id, group_id, setting):
    """Make the user_id requested an admin of the requested group.
    Can take either a single integer user_id or a list of same"""
    member = Member.query.filter(Member.user_id == user_id,
                                 Member.group_id == group_id).one()
    member.admin = setting
    db.session.commit()


# GROUP


def get_group(group_id):
    """Return the group with the requested id."""
    return Group.query.get(group_id)


def search_groups(querystring):
    """Return all groups whose name is like the query string."""
    return set(Group.query.filter(
        Group.name.like("%" + querystring + "%")).all())
