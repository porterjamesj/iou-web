from __future__ import division
from collections import defaultdict
from copy import deepcopy
from itertools import combinations
from app.models import CLEAR_ALL

#These functions work on graphs, which are dicts of dicts that can be thought
#of as graph[creditor][debtor] = amount.


def build_graph(users, transactions):
    """Given lists of users and transactions, return the corresponding
    graph. Transactions must be ordered by time for this to work correctly."""
    # check that the transactions are all for the one group
    if len({trans.group_id for trans in transactions}) > 1:
        raise RuntimeError("Some transactions not in requested group.")
    # should maybe add a sanity check that all users in the
    # transactions are in the user list; this could get expensive for
    # many transactions, it may be better to let the caller handle it

    # the dictionary we will build up and return
    emptygraph = {u.id: defaultdict(int) for u in users}
    graph = deepcopy(emptygraph)
    for trans in transactions:
        if trans.kind == CLEAR_ALL:
            graph = deepcopy(emptygraph)
        else:
            graph[trans.to_id][trans.from_id] += float(trans.amount)
    # simplify graph
    return simplify(graph)


def get_flows(graph):
    """Given a graph, return a set of (name, flow) tuples indicating the flow
    in or out of each person in the graph. Flow is positive for a net creditor
    and negative for a net debtor. """
    nodeflows = {person: 0.0 for person in graph}
    for person1 in graph:
        for person2 in graph[person1]:
            value = graph[person1][person2]
            nodeflows[person1] += value
            nodeflows[person2] -= value
    return set(nodeflows.items())


def add(graph, creditor, debtors, amount):
    """Return a new graph with the specified debt added to it. Debtors should
    be either a key in the dict or a list of keys."""
    newgraph = deepcopy(graph)  # the graph we will return
    if isinstance(debtors, list):
        # check that all the debtors actually exist
        for debtor in debtors:
            if debtor not in newgraph.keys():
                raise KeyError("debtor not found.")
        # go ahead and add split / add the debt
        each_amount = float(amount) / len(debtors)
        for debtor in debtors:
            if debtor != creditor:
                # The above line is confusing, it is there to ensure
                # that splits in which one person buys something for a
                # group that includes them (and therefore is both a
                # debtor and the creditor) work correctly.
                newgraph[creditor][debtor] += each_amount
    else:  # the debtor is a key in the graph
        # check that the debtor exists
        if debtors not in newgraph.keys():
            raise KeyError("debtor not found.")
        # go ahead and add it
        newgraph[creditor][debtors] += float(amount)
    return newgraph


def flows2graph(flows):
    """Given a set of n flows for a connected graph, construct the
    simplest possible graph that satisfies their values. (this graph
    will have n-1 edges)"""
    # Split flows into positive and negative and sort each
    pos_flows = [list(flow) for flow in flows if flow[1] > 0]
    neg_flows = [list(flow) for flow in flows if flow[1] < 0]
    pos_flows.sort(key=lambda t: -t[1])
    neg_flows.sort(key=lambda t: t[1])
    # Now build the new optimal debt graph
    graph = {flow[0]: defaultdict(float) for flow in flows}
    while pos_flows and neg_flows:
        credit = pos_flows[0][1]
        debit = neg_flows[0][1]
        creditor = pos_flows[0][0]
        debtor = neg_flows[0][0]
        # conditional says keep going until both are empty
        if abs(credit) == abs(debit):
            graph[creditor][debtor] += credit
            neg_flows.pop(0)
            pos_flows.pop(0)
        if abs(credit) < abs(debit):
            graph[creditor][debtor] += credit
            pos_flows.pop(0)
            neg_flows[0][1] += credit
        if abs(credit) > abs(debit):
            graph[creditor][debtor] += abs(debit)
            neg_flows.pop(0)
            pos_flows[0][1] += debit
    return graph


def partition(flows, n=2):
    """Given a set of flows, return the longest list of zero-sum
    subsets that covers the original set. Can specify the minimum
    size of a subset with `n`."""
    for subset in combinations(flows, n):
        if sum(flow[1] for flow in subset) == 0.0:
            # this is a zero-sum node
            # recurse
            subset = set(subset)
            return [subset] + partition(flows.difference(subset), n)
    # if there are no zero-sum subsets, first check if we have found
    # all subsets
    if n >= len(flows)//2:
        # there are no more left to find
        return [flows]
    else:
        return partition(flows, n+1)


def simplify(graph):
    """Simplify a graph. This is defined as minimizing the number of edges
    (transactions) and then minimizing |total edge weight| (the total amount of
    money that has to change hands)."""
    # get the flows in or out of each node
    flows = get_flows(graph)
    # as a preprocessing step, filter out the zero-sum nodes
    zeroflows = {flow for flow in flows if flow[1] == 0.0}
    nonzeroflows = flows.difference(zeroflows)
    # partition the graph into the maximum possible number of zero-sum subsets
    subsets = partition(nonzeroflows)
    # once we have the subsets, build the simplest possible graph for each
    newgraphs = [flows2graph(subset) for subset in subsets]
    # merge all the constructed graphs together into one dict
    finalgraph = {k: v for graph in newgraphs for k, v in graph.items()}
    # append all the zero nodes
    for node in zeroflows:
        finalgraph[node[0]] = {}
    return finalgraph


def display_graph(users, graph):
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
