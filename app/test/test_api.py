from flask import json, request
from flask.ext.testing import TestCase
from app.models import User,Group,Member,Trans
from app import app, api
from mock import Mock

class APIBase(TestCase):
    """Base class for all api tests to inherit from."""
    def create_app(self):
        app.config['LOGIN'] = False
        return app


class TestAddTrans(APIBase):
    @classmethod
    def setup_class(self):
        """Mock services layer, and request."""
        self.srvmock = Mock()
        data = json.dumps({"group_id":1,
                           "from":[1],
                           "to_id":[2],
                           "amount":20,
                           "kind": "debt"})
        self.fake_request = app.test_request_context(data = data,
                                                     content_type =
                                                     "application/json")


    def setUp(self):
        """Reset the mock values for each test."""
        self.srvmock.users_exist.return_value = [User(),User()]
        self.srvmock.group_exists.return_value = Group()
        self.srvmock.users_in_group.return_value = True
        self.srvmock.add_transaction.return_value = None

    def test_succeed_normally(self):
        with self.fake_request:
            print api.addtrans(dbsrv = self.srvmock).get_data()
            assert "0" in api.addtrans(dbsrv = self.srvmock).get_data()

    def test_fail_if_user_does_not_exist(self):
        with self.fake_request:
            self.srvmock.users_exist.return_value = False
            assert "1" in api.addtrans(dbsrv = self.srvmock).get_data()

    def test_fail_if_group_does_not_exist(self):
        with self.fake_request:
            self.srvmock.group_exists.return_value = False
            assert "2" in api.addtrans(dbsrv = self.srvmock).get_data()

    def test_fail_if_user_is_not_in_group(self):
        with self.fake_request:
            self.srvmock.users_in_group.return_value = False
            assert "3" in api.addtrans(dbsrv = self.srvmock).get_data()

class TestClearAll(APIBase):

    @classmethod
    def setup_class(self):
        """Mock services layer, and request."""
        self.srvmock = Mock()
        self.fake_request = app.test_request_context()

    def setUp(self):
        self.srvmock.group_exists.return_value = Group()
        self.srvmock.user_is_admin.return_value = True

    def test_succeed_normally(self):
        with self.fake_request:
            assert "0" in api.clearall(1,dbsrv = self.srvmock).get_data()

    def test_fail_if_group_does_not_exist(self):
        with self.fake_request:
            self.srvmock.group_exists.return_value = False
            assert "2" in api.clearall(1,dbsrv = self.srvmock).get_data()

    def test_fail_if_current_user_is_not_admin(self):
        with self.fake_request:
            self.srvmock.user_is_admin.return_value = False
            assert "4" in api.clearall(1,dbsrv = self.srvmock).get_data()

class TestAddAdmin(APIBase):
    @classmethod
    def setup_class(self):
        """Mock services layer, and request."""
        self.srvmock = Mock()
        data = json.dumps({"group":1,
                           "user":[1]})
        self.fake_request = app.test_request_context(data = data,
                                                     content_type =
                                                     "application/json")

    def setUp(self):
        self.srvmock.group_exists.return_value = Group()
        self.srvmock.users_exist.return_value = [User()]
        self.srvmock.users_in_group.return_value = True
        self.srvmock.user_is_admin.return_value = False

    def test_succeed_normally(self):
        with self.fake_request:
            assert "0" in api.addadmin(dbsrv = self.srvmock).get_data()

    def test_fail_if_user_does_not_exist(self):
        with self.fake_request:
            self.srvmock.users_exist.return_value = False
            assert "1" in api.addadmin(dbsrv =self.srvmock).get_data()

    def test_fail_if_group_does_not_exist(self):
        with self.fake_request:
            self.srvmock.group_exists.return_value = False
            assert "2" in api.addadmin(dbsrv =self.srvmock).get_data()

    def test_fail_if_user_is_admin(self):
        with self.fake_request:
            self.srvmock.user_is_admin.return_value = True
            assert "5" in api.addadmin(dbsrv =self.srvmock).get_data()

class TestResign(APIBase):
    @classmethod
    def setup_class(self):
        """Mock services layer, and request."""
        self.srvmock = Mock()
        self.fake_request = app.test_request_context()

    def setUp(self):
        self.srvmock.group_exists.return_value = True
        self.srvmock.users_in_group.return_value = True
        self.srvmock.user_is_admin.return_value = True

    def test_succeed_normally(self):
        with self.fake_request:
            assert "0" in api.resign(1,dbsrv = self.srvmock).get_data()

    def test_fail_if_group_does_not_exist(self):
        with self.fake_request:
            self.srvmock.group_exists.return_value = False
            assert "2" in api.resign(1,dbsrv = self.srvmock).get_data()

    def test_fail_if_user_not_in_group(self):
        with self.fake_request:
            self.srvmock.users_in_group.return_value = False
            assert "3" in api.resign(1,dbsrv = self.srvmock).get_data()

    def test_fail_if_user_not_admin(self):
        with self.fake_request:
            self.srvmock.user_is_admin.return_value = False
            assert "6" in api.resign(1,dbsrv = self.srvmock).get_data()

class TestSearchUsers(APIBase):
    @classmethod
    def setup_class(self):
        self.srvmock = Mock()
        self.srvmock.search_users.return_value = [User(name="james",id=3,
                                                       email="james@gmail.com")]
        self.fake_request = app.test_request_context()

    def test_jsonifys_users(self):
        with self.fake_request:
            assert "james@gmail" in api.search_users("james",
                                                     dbsrv = self.srvmock).get_data()
            assert "3" in api.search_users("james",
                                           dbsrv = self.srvmock).get_data()
