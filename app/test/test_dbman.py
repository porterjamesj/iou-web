from app.models import User, Group, Trans, Member, DEBT, PAYMENT, CLEAR_ALL
import app.services.db as dbsrv
from flask.ext.testing import TestCase
from app import app,db

class DbBase(TestCase):
    def create_app(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        return app

    def setUp(self):
        # make the tables
        db.create_all()

        # make some users
        names = ['James', 'Will']

        emails = ['james@gmail.com', 'will@gmail.com']

        for name,email in zip(names,emails):
            user = User(name = name, email = email, dummy = False)
            user.set_password('pass')
            db.session.add(user)
            db.session.commit()

        self.james = User.query.get(1)
        self.will = User.query.get(2)

        # make duskmantle group and assign members
        self.duskmantle = Group(name = 'Duskmantle, House of Shadows')
        db.session.add(self.duskmantle)
        db.session.commit()

        # make me an admin in duskmantle
        james_dm = Member(user_id=1,group_id=1,admin=True)
        db.session.add(james_dm)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()


class TestUsersExist(DbBase):
    """Test that the db manipulation services work correctly."""

    def test_gets_users(self):
        assert dbsrv.users_exist([1]) == [User.query.get(1)]

    def test_returns_false_if_users_not_found(self):
        assert dbsrv.users_exist([30]) == False
        assert dbsrv.users_exist([1,30]) == False


class TestGroupExists(DbBase):
    def test_gets_groups(self):
        assert dbsrv.group_exists(1) == Group.query.get(1)

    def test_returns_false_if_groups_not_found(self):
        assert dbsrv.group_exists(30) == False

class TestUsersInGroup(DbBase):
    def test_returns_true_if_user_in_group(self):
        """Should return true if users are in the group."""
        assert dbsrv.users_in_group([self.james],self.duskmantle) == True

    def test_returns_false_if_user_not_in_group(self):
        """Should return false if users are not in the group."""
        assert dbsrv.users_in_group([self.will],self.duskmantle) == False

class TestUserIsAdmin(DbBase):
    def test_returns_true_if_user_is_admin(self):
        assert dbsrv.user_is_admin(self.james,self.duskmantle) == True

    def test_retuns_false_if_user_is_not_admin(self):
        assert dbsrv.user_is_admin(self.will,self.duskmantle) == False

class TestSetAdmins(DbBase):
    def test_set_admins(self):
        dbsrv.set_admins([self.james],self.duskmantle,False)
        assert Member.query.filter(Member.user_id == self.james.id,
                                   Member.group_id == self.duskmantle.id).one()\
                                   .admin == False

class TestAddTrans(DbBase):
    def test_add_trans(self):
        dbsrv.add_transaction(1,1,2,20,DEBT)
        assert len(Trans.query.all()) == 1
        assert Trans.query.all()[0].amount == 20

class TestSearchUsers(DbBase):
    def test_finds_users(self):
        assert dbsrv.search_users("james") == set([self.james])
        assert dbsrv.search_users("gmail") == set([self.james,self.will])

    def test_fails_to_find_users(self):
        assert dbsrv.search_users("nope") == set([])

class TestSearchGroups(DbBase):
    def test_finds_groups(self):
        assert dbsrv.search_groups("Dusk") == set([self.duskmantle])

    def test_fails_to_find_groups(self):
        assert dbsrv.search_groups("nope") == set([])
