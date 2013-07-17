from app.models import User, Group, Trans, Member, DEBT, PAYMENT, CLEAR_ALL
import app.services.db as dbsrv
from flask.ext.testing import TestCase
from app import app,db

class TestDb(TestCase):
    """Test that the db manipulation services work correctly."""

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

    def test_users_exist_true(self):
        """users_exist should return the user correctly."""
        assert dbsrv.users_exist([1]) == [User.query.get(1)]

    def test_users_exist_false(self):
        """users_exist should return false correctly."""
        assert dbsrv.users_exist([30]) == False
        assert dbsrv.users_exist([1,30]) == False

    def test_group_exists_true(self):
        """Should return true when the group exists."""
        assert dbsrv.group_exists(1) == Group.query.get(1)

    def test_group_exists_false(self):
        """Should return fase when the group doesn't exist."""
        assert dbsrv.group_exists(30) == False

    def test_users_in_group_true(self):
        """Should return true if users are in the group."""
        assert dbsrv.users_in_group([self.james],self.duskmantle) == True

    def test_users_in_group_false(self):
        """Should return false if users are not in the group."""
        assert dbsrv.users_in_group([self.will],self.duskmantle) == False

    def test_user_is_admin_true(self):
        """Should return true if the user is an admin."""
        assert dbsrv.user_is_admin(self.james,self.duskmantle) == True

    def test_user_is_admin_false(self):
        """Should return false if the user is not an admin."""
        assert dbsrv.user_is_admin(self.will,self.duskmantle) == False

    def test_set_admins(self):
        """Setting admin status should work."""
        dbsrv.set_admins([self.james],self.duskmantle,False)
        assert Member.query.filter(Member.user_id == self.james.id,
                                   Member.group_id == self.duskmantle.id).one()\
                                   .admin == False

    def test_add_trans(self):
        """Transactions should be added correctly."""
        dbsrv.add_transaction(1,1,2,20,DEBT)
        assert len(Trans.query.all()) == 1
        assert Trans.query.all()[0].amount == 20
