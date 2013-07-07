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

    def test_basic(self):
        """The graph should be built correctly in simple cases."""
        dg = srv.build_graph(self.transactions)
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
        dg = srv.build_graph(self.transactions)
        print dg.graph
        assert dg.graph == {3: {},
                            2: {3: 100.0},
                            1: {}}

    @raises(RuntimeError)
    def test_error(self):
        """Should error if all transactions are not in the same group."""
        self.transactions.append(
            Trans(group_id=2,to_id=2,from_id=3,amount=100,kind=DEBT))
        srv.build_graph(self.transactions)
