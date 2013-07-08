from app.models import User, Group, Trans, Member, DEBT, PAYMENT, CLEAR_ALL
import app.services as srv
from nose.tools import raises

class TestBuildGraph():
    """Test building a graph from a list of transactions."""

    def setUp(self):
        self.transactions = [
            Trans(group_id=1,to_id=1,from_id=3,amount=2,kind=DEBT),
            Trans(group_id=1,to_id=1,from_id=3,amount=3,kind=DEBT),
            Trans(group_id=1,to_id=2,from_id=1,amount=10,kind=DEBT),
            Trans(group_id=1,to_id=3,from_id=2,amount=15,kind=DEBT),
            Trans(group_id=1,to_id=2,from_id=3,amount=5,kind=DEBT)
        ]

        self.users = [
            User(id=1, name="alice"),
            User(id=2, name="bob"),
            User(id=3, name="charlie")
        ]

    def test_basic(self):
        """The graph should be built correctly in simple cases."""
        dg = srv.build_graph(self.users,self.transactions)
        assert dg.graph == {3: {1: 5.0},
                            2: {},
                            1: {}}

    def test_clear_all(self):
        """Graph should ignore everything that happens before the last
        CLEAR_ALL."""
        self.transactions.extend([
            Trans(group_id=1,kind=CLEAR_ALL),
            Trans(group_id=1,to_id=2,from_id=3,amount=100,kind=DEBT)
            ])
        dg = srv.build_graph(self.users,self.transactions)
        print dg.graph
        assert dg.graph == {3: {},
                            2: {3: 100.0},
                            1: {}}

    def test_no_transactions(self):
        """Should return empty dict of users when there are no transactions."""
        dg = srv.build_graph(self.users,[]) == {1: {}, 2: {}, 3:{}}

    @raises(RuntimeError)
    def test_error(self):
        """Should error if all transactions are not in the same group."""
        self.transactions.append(
            Trans(group_id=2,to_id=2,from_id=3,amount=100,kind=DEBT))
        srv.build_graph(self.users,self.transactions)

class TestDisplayGraph():
    """Test converting a graph in terms of user ids to a graph in terms of
    user names, suitable for displaying on the page."""

    def setUp(self):
        self.graph = {1: {2: 20, 3:5},
                      2: {1:10},
                      3: {}}
        self.users = [
            User(id=1,name="alice"),
            User(id=2,name="bob"),
            User(id=3,name="charlie")
        ]

    def test_basic(self):
        """display_graph should work as expected on simple inputs."""
        assert srv.display_graph(self.users,
                                 self.graph) == {"alice": {"bob": 20, "charlie":5},
                                                 "bob": {"alice":10},
                                                 "charlie": {}}

    @raises(KeyError)
    def test_error(self):
        """display_graph should raise an error if the users list does not contain
        all the users in the graph."""
        del self.graph[0]
        srv.display_graph(self.users,self.graph)
