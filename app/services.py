from app.models import User, Group, Member, Trans, DEBT, PAYMENT, CLEAR_ALL
from debtgraph import DebtGraph
from collections import defaultdict
from copy import deepcopy

def add_transaction(group_id, from_id, to_id, amount, debt):
    """Add the specified transaction to the database."""
    newtrans = Trans(group_id = group_id,
                     from_id = from_id,
                     to_id = to_id,
                     amount = amount,
                     kind = debt)
    db.session.add(newtrans)
    db.session.commit()

def build_graph(users,transactions):
    """Given lists of users and transactions, return the corresponding
    debtgraph."""
    # check that the transactions are all for the one group
    if len({trans.group_id for trans in transactions}) > 1:
            raise RuntimeError("Some transactions not in requested group.")
    # should maybe add a sanity check that all users in the
    # transactions are in the user list; this could get expensive for
    # many transactions, it may be better to let the caller handle it

    # the dictionary we will build up and return
    emptygraph = {u.id: defaultdict(int) for u in users}
    print emptygraph
    graph = deepcopy(emptygraph)
    for trans in transactions:
        if trans.kind == CLEAR_ALL:
            graph = deepcopy(emptygraph)
        else:
            graph[trans.to_id][trans.from_id] += float(trans.amount) # from Decimal
    # simplify graph
    dg = DebtGraph(graph)
    dg.collapse()
    return dg

def display_graph(users,graph):
    """Converts a graph in terms of user ids to one in terms of usernames,
    suitable for display. Requires a list of users to use for the mapping."""
    dispgraph = {}
    namemap = {u.id: u.name for u in users}
    for u in users:
        dispgraph[u.name] = {}
        for subid in graph[u.id]:
            try:
                dispgraph[u.name][namemap[subid]] = graph[u.id][subid]
            except:
                raise KeyError("User list has no mapping for this user.")
    return dispgraph
