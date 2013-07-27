from app.models import User, Group, Trans, Member, DEBT, CLEAR_ALL
import app.services.db as dbsrv
from flask.ext.testing import TestCase
from app import app, db
from app import errors as err
from nose.tools import raises


class DbBase(TestCase):
    def create_app(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        return app

    def setUp(self):
        # make the tables
        db.create_all()

        # make some users
        names = ['James', 'Will', 'John']

        emails = ['james@gmail.com', 'will@gmail.com', 'John@gmail.com']

        for name, email in zip(names, emails):
            user = User(name=name, email=email, dummy=False)
            user.set_password('pass')
            db.session.add(user)
            db.session.commit()

        self.james = User.query.get(1)
        self.will = User.query.get(2)
        self.john = User.query.get(3)

        # make duskmantle group and assign members
        self.duskmantle = Group(name='Duskmantle, House of Shadows')
        db.session.add(self.duskmantle)
        will_dm = Member(user_id=2, group_id=1, admin=False)
        db.session.add(will_dm)
        db.session.commit()

        # make me an admin in duskmantle
        james_dm = Member(user_id=1, group_id=1, admin=True)
        db.session.add(james_dm)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()


class TestAddTransaction(DbBase):
    def test_succeeds_normally(self):
        dbsrv.add_transaction(1, 1, 2, 20, DEBT)
        newtrans = Trans.query.get(1)
        assert newtrans.amount == 20

    @raises(err.UsersNotInGroupError)
    def test_fail_is_users_not_in_group(self):
        dbsrv.add_transaction(1, 3, 2, 20, DEBT)


class TestClearAll(DbBase):
    def test_succeeds_normally(self):
        dbsrv.clear_all(1)
        newtrans = Trans.query.get(1)
        assert newtrans.kind == CLEAR_ALL

    @raises(err.GroupDoesNotExistError)
    def test_fails_if_group_does_not_exist(self):
        dbsrv.clear_all(2)


class TestChangeUser(DbBase):
    def test_succeeds_normally(self):
        dbsrv.change_user(1, name="test", email="test@test.com")
        assert self.james.name == "test"
        assert self.james.email == "test@test.com"

    @raises(err.UserDoesNotExistError)
    def test_fails_if_user_does_not_exist(self):
        dbsrv.change_user(4, name="test")


class TestSearchUsers(DbBase):
    def test_succeeds_normally(self):
        result = dbsrv.search_users("j")
        assert self.james in result
        assert self.john in result

    def test_finds_nothing(self):
        result = dbsrv.search_users("z")
        assert result == set([])


class TestUsersInGroup(DbBase):
    def test_returns_true_correctly(self):
        assert dbsrv.users_in_group([1, 2], 1) is True
        assert dbsrv.users_in_group(1, 1) is True

    def test_returns_false_correctly(self):
        assert dbsrv.users_in_group([1, 3], 1) is False


class TestAddMember(DbBase):
    def test_succeeds_normally(self):
        dbsrv.add_member(3, 1)
        assert self.john in self.duskmantle.members

    @raises(err.MemberAlreadyError)
    def test_fails_if_user_already_in_group(self):
        dbsrv.add_member(1, 1)


class TestSetAdmin(DbBase):
    def test_succeeds_normally(self):
        dbsrv.set_admin(2, 1, True)
        assert self.will.member[0].admin is True


class TestSearchGroups(DbBase):
    def test_succeeds_normally(self):
        res = dbsrv.search_groups("d")
        assert self.duskmantle in res

    def test_finds_nothing(self):
        assert dbsrv.search_groups("z") == set([])
