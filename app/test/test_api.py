from flask import json
from flask.ext.testing import TestCase
from flask.ext.login import LoginManager
from app.models import User, Group
from app import app, api
from app import errors as err
from mock import Mock
from nose.tools import raises
from werkzeug.exceptions import NotFound


class APIBase(TestCase):
    def create_app(self):
        app.config['TESTING'] = True
        login_manager = LoginManager()
        login_manager.init_app(app)  # this has to happen to turn login off
        return app


class ParsesJson():
    @raises(err.JSONParseError)
    def test_fail_if_bad_json(self):
        with app.test_request_context(data="garbage"):
            api.post_trans(dbsrv=self.sm)


class TestPostTrans(APIBase, ParsesJson):
    @classmethod
    def setup_class(self):
        self.sm = Mock()  # mock for the database services layer
        data = json.dumps({"group_id": 1,
                           "from_ids": [1],
                           "to_id": [2],
                           "amount": 20,
                           "kind": "debt"})
        self.fake_request = app.test_request_context(data=data,
                                                     content_type=
                                                     "application/json")

    def setUp(self):
        self.sm.get_users.return_value = [User(), User()]
        self.sm.get_groups.return_value = Group()
        self.sm.users_in_group.return_value = True
        self.sm.add_transaction.return_value = None

    def test_succeed_normally(self):
        with self.fake_request:
            self.assertStatus(api.post_trans(dbsrv=self.sm), 200)


class TestSearchUsers(APIBase, ParsesJson):
    @classmethod
    def setup_class(self):
        self.sm = Mock()  # mock for the database services layer
        self.fake_request = app.test_request_context("?query=testquery")

    def setUp(self):
        self.sm.search_users.return_value = [User()]

    def test_succeed_normally(self):
        with self.fake_request:
            self.assertStatus(api.search_users(dbsrv=self.sm), 200)


class TestGetUser(APIBase):
    @classmethod
    def setup_class(self):
        self.sm = Mock()  # mock for the database services layer
        self.fake_request = app.test_request_context()

    def test_succeed_normally(self):
        self.sm.get_user.return_value = User()
        with self.fake_request:
            self.assertStatus(api.get_user(1, dbsrv=self.sm), 200)

    @raises(NotFound)
    def test_404_if_no_such_user(self):
        self.sm.get_user.return_value = None
        with self.fake_request:
            api.get_user(1, dbsrv=self.sm)


class TestPutUser(APIBase, ParsesJson):
    @classmethod
    def setup_class(self):
        self.sm = Mock()
        data = json.dumps({"name": "test"})
        self.fake_request = app.test_request_context(data=data,
                                                     content_type=
                                                     "application/json")

    def test_succeed_normally(self):
        self.sm.change_user.return_value = None
        with self.fake_request:
            self.assertStatus(api.put_user(1, dbsrv=self.sm), 200)


class TestSearchGroups(APIBase, ParsesJson):
    @classmethod
    def setup_class(self):
        self.sm = Mock()

    def setUp(self):
        self.sm.search_groups.return_value = [Group()]

    def test_succeed_normally(self):
        with app.test_request_context("?query=testquery"):
            self.assertStatus(api.search_groups(dbsrv=self.sm), 200)


class TestGetGroup(APIBase):
    @classmethod
    def setup_class(self):
        self.sm = Mock()

    def test_succeed_normally(self):
        self.sm.get_group.return_value = Group()
        self.assertStatus(api.get_group(1, dbsrv=self.sm), 200)

    @raises(NotFound)
    def test_fail_if_group_not_found(self):
        self.sm.get_group.return_value = None
        api.get_group(1, dbsrv=self.sm)


class TestPutGroup(APIBase, ParsesJson):
    @classmethod
    def setup_class(self):
        self.sm = Mock()
        data = json.dumps({"name": "test"})
        self.fake_request = app.test_request_context(data=data,
                                                     content_type=
                                                     "application/json")

    def test_succeed_normally(self):
        with self.fake_request:
            self.assertStatus(api.put_group(1, dbsrv=self.sm), 200)


class TestIsMember(APIBase):
    @classmethod
    def setup_class(self):
        self.sm = Mock()

    def test_succeed_normally(self):
        self.sm.users_in_group.return_value = True
        self.assertStatus(api.is_member(1, 1, dbsrv=self.sm), 200)

    @raises(NotFound)
    def test_404_if_no_such_member(self):
        self.sm.users_in_group.return_value = False
        api.is_member(1, 1, dbsrv=self.sm)


class TestNewMember(APIBase):
    @classmethod
    def setup_class(self):
        self.sm = Mock()

    def test_succeed_normally(self):
        self.assertStatus(api.new_member(1, 1, dbsrv=self.sm), 200)


class TestPutSelf(APIBase, ParsesJson):
    @classmethod
    def setup_class(self):
        self.sm = Mock()
        data = json.dumps({"action": "resign"})
        self.fake_request = app.test_request_context(data=data,
                                                     content_type=
                                                     "application/json")

    def test_succeed_normally(self):
        with self.fake_request:
            self.assertStatus(api.put_self(1, dbsrv=self.sm), 200)
