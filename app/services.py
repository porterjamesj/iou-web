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

def build_graph(transactions):
    """Given a list of transactions, return the corresponding debtgraph."""
    # check that the transactions are all for the same group
    if not len({trans.group_id for trans in transactions}) == 1:
            raise RuntimeError("Some transactions not in the same group.")
    # the dictionary we will build up and return
    emptygraph = {id:defaultdict(int)
                  for id in {trans.to_id
                             for trans in transactions if trans.kind != CLEAR_ALL}}
    graph = deepcopy(emptygraph)
    for trans in transactions:
        if trans.kind == CLEAR_ALL:
            graph = deepcopy(emptygraph)
        else:
            graph[trans.to_id][trans.from_id] += trans.amount
    # simplify graph
    dg = DebtGraph(graph)
    dg.collapse()
    return dg

def display_graph(graph,users):
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
