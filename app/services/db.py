from app.models import Trans, User, Member, Group
from app import db
from time import time
import app.errors as err


def add_transaction(group_id, from_id, to_id, amount, kind):
    """Add the specified transaction to the database."""
    # check that that the users are members of the group
    users_in_group([from_id, to_id], group_id)
    # now add the transaction
    newtrans = Trans(group_id=group_id,
                     from_id=from_id,
                     to_id=to_id,
                     amount=amount,
                     time=time(),
                     kind=kind)
    db.session.add(newtrans)
    db.session.commit()


# def get_users(user_ids):
#     """Given a list of user ids, return a list of them if they do
#     exist, otherwise raise an error."""
#     users = User.query.filter(User.id.in_(user_ids)).all()
#     if len(users) != len(user_ids):
#         raise err.UserNotFoundError("No such user(s)")
#     else:
#         return users


# def get_group(group_id):
#     """Return the group if it exists, throw an error otherwise."""
#     group = Group.query.get(group_id)
#     if group is None:
#         raise err.GroupNotFoundError("No such group")
#     else:
#         return group


def users_in_group(user_ids, group_id):
    """Return true if all users are members of the group, false
    otherwise."""
    members = Member.query.filter(Member.group_id == group_id,
                                  Member.user_id.in_(user_ids)).all()
    print members
    if len(members) == len(user_ids):  # someone is not in the group
        return True
    else:
        return False
        # raise err.UsersNotInGroupError("Users not in requested group")


# def user_is_admin(user, group):
#     """Return true if the user is an admin for the group, false
#     otherwise."""
#     admins = Member.query.filter(Member.admin is True,
#                                  Member.group_id == group.id).all()
#     if user.id in [admin.user_id for admin in admins]:
#         return True
#     else:
#         return False


def add_member(user_id, group_id):
    """Make the user a member of the group, but not an admin."""
    if users_in_group([user_id], group_id):
        raise err.MemberAlreadyError(
            "Users is already a member of this group.")
    else:
        member = Member(user_id=user_id,
                        group_id=group_id,
                        admin=False)
        db.session.add(member)
        db.session.commit()


def set_admins(user_ids, group_id, setting):
    """Set the admin status of each user in the group to the requested
    setting. If the admin status is not being changed, an error is thrown"""
    members = Member.query.filter(Member.user_id.in_(user_ids),
                                  Member.group_id == group_id)
    for member in members:
        if member.admin == setting:
            raise err.SetAdminError("Admin status is not being changed.")
        else:
            member.admin = setting
    db.session.commit()


def search_users(querystring):
    """Return all the users whose name or email is like the query string."""
    foundname = User.query.filter(User.name.like("%" +
                                                 querystring + "%")).all()
    foundemail = User.query.filter(User.email.like("%" +
                                                   querystring + "%")).all()
    return set(foundname+foundemail)


def search_groups(querystring):
    """Return all groups whose name is like the query string."""
    return set(Group.query.filter(Group.name.like("%" +
                                                  querystring + "%")).all())
