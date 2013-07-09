from app.models import User, Group, Trans, Member, DEBT, PAYMENT, CLEAR_ALL
import app.services as srv
from nose.tools import raises
from collections import defaultdict

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
        print  srv.build_graph(self.users,
                               self.transactions)
        assert srv.build_graph(self.users,
                               self.transactions) == {3: {1: 5.0},
                                                      2: {},
                                                      1: {}}
    def test_clear_all(self):
        """Graph should ignore everything that happens before the last
        CLEAR_ALL."""
        self.transactions.extend([
            Trans(group_id=1,kind=CLEAR_ALL),
            Trans(group_id=1,to_id=2,from_id=3,amount=100,kind=DEBT)
            ])
        assert  srv.build_graph(self.users,
                                self.transactions) ==  {3: {},
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

class TestManipulate():
    """Test mundane graph manipulation functions."""
    def setUp(self):
        self.graph = {1: defaultdict(float,{2:20, 3:5}),
                      2: defaultdict(float,{1:10}),
                      3: defaultdict(float,{})}

    def test_addition_normal(self):
        """Adding to an already existing debt should increase it."""
        assert srv.add(self.graph,1,2,5) == {1: {2: 25,3: 5},
                                             2: {1: 10},
                                             3: {}}

    def test_addition_split(self):
        """Adding a debt with multiple debtors should split the debt."""
        assert srv.add(self.graph,3,[1,2],10) == {1: {2: 20, 3:5},
                                                  2: {1: 10},
                                                  3: {1: 5,2: 5}}

    def test_addition_split_self(self):
        """Adding a debt with multiple debtors including the creditor should
        spilt the debt between everyone except the creditor."""
        assert srv.add(self.graph,3,[1,2,3],15) == {1: {2: 20, 3:5},
                                                    2: {1: 10},
                                                    3: {1: 5,2: 5}}


class TestEasyGraph():
    """Test simplifcation of easy graphs."""
    def setUp(self):
        self.graph = {1: defaultdict(float,{2: 20, 3:5}),
                      2: defaultdict(float,{1:10}),
                      3: defaultdict(float,{})}
        self.flows = set([(1,15), (2,-10), (3,-5)])
        self.simplegraph = { 1: defaultdict(float,{2: 10, 3: 5}),
                             2: defaultdict(float,{}),
                             3: defaultdict(float,{}) }

    def test_get_flows(self):
        """Flows in and out of each node should be calculated correctly."""
        assert srv.get_flows(self.graph) == self.flows

    def test_flows2graph(self):
        """Simple flow sets should be correctly converted into graphs."""
        assert srv.flows2graph(self.flows) == self.simplegraph

    def test_simplify_no_subgraphs(self):
        """Easy graphs with no subgraphs should simplify correctly."""
        assert srv.simplify(self.graph) == self.simplegraph


class TestHardGraph():
    """Test simplifcation of more complex graphs (with subgraphs), as well as
    edge cases, bugs, etc."""
    def setUp(self):
        self.graph = {1: defaultdict(float,{2: 20, 3:5}),
                      2: defaultdict(float,{1:10}),
                      3: defaultdict(float,{}),
                      4: defaultdict(float,{5: 15}),
                      5: defaultdict(float,{})}
        self.flows = set([(1,15), (2,-10), (3,-5), (4,15), (5,-15)])
        self.simplegraph = { 1: defaultdict(float,{2: 10, 3: 5}),
                             2: defaultdict(float,{}),
                             3: defaultdict(float,{}),
                             4: defaultdict(float,{5: 15}),
                             5: defaultdict(float,{}) }

    # this is all the same as above, might refactor later
    def test_get_flows(self):
        """Flows in and out of each node should be calculated correctly."""
        assert srv.get_flows(self.graph) == self.flows

    def test_flows2graph(self):
        """Harder flow sets should be correctly converted into graphs."""
        assert srv.flows2graph(self.flows) == self.simplegraph

    def test_simplify_no_subgraphs(self):
        """Harder graphs with subgraphs should simplify correctly."""
        assert srv.simplify(self.graph) == self.simplegraph

    def test_simplify_bug(self):
        print  srv.simplify({1: {3: 5.0},
                             2: {1: 10.0, 3: 5.0},
                             3: {2: 15.0}})
        assert srv.simplify({1: {3: 5.0},
                             2: {1: 10.0, 3: 5.0},
                             3: {2: 15.0}}) ==  {3: {1: 5.0},
                                                      2: {},
                                                      1: {}}


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
