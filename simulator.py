"""
Simualates a network running.  Initializes all properties of the network and the schedule and topology that will be used
for the current exercise.

Usage:
    ARGS:
        --type (what type of consensus protocol to run: proof_of_work (pow), proof_of_stake (pos), or centralized (c))
        --nodes (number of nodes to run experiment with)
        --schedule (file name of the schedule that will run in a format that has time stamp mapped to a list of transactions
                    that will happen)
        --topo (topology to use; equadistant sets all nodes an equal distance apart)
"""
from argparse import ArgumentParser
import json
import os
import time

from block import Block
from network import CentralizedNetwork, ProofOfStakeNetwork, ProofOfWorkNetwork
from node import Node
from util import exponential_latency


parser = ArgumentParser(description="Bitcoin network basic simulation")
parser.add_argument('--type',
                    type=str,
                    help="What type of protocol to run (proof_of_work (pow), proof_of_stake (pos), or centralized (c)",
                    default="pow")
parser.add_argument('--nodes',
                    type=int,
                    help="Number of nodes to launch",
                    default=5)
parser.add_argument('--schedule',
                    type=str,
                    help="File name of the schedule for the current experiment",
)
parser.add_argument('--topo',
                    type=str,
                    help="Topology for  current experiment",
                    default="equadistant"
)
parser.add_argument('--name',
                    type=str,
                    help="Name of current experiment",
)
args = parser.parse_args()


def init_nodes(net, n=3): 
    """
    Initialize the passed in number of nodes for our network
    """
    genesis_block = Block(block_id=0, data="genesis block", timestamp=time.time())
    nodes = []
    for i in range(n):
        nodes.append(Node(i, net, genesis_block))
    return nodes

def clean_up_json(data):
    """
    Takes a json with all values typed string, and re-assigns them to be of the correct type
    (integer keys, with lists of [int, str])
    """
    clean_data = {}
    for k, v in data.items():
        new_v = []
        for timestamp, txn_data in v:
            new_v.append((int(timestamp), txn_data))
        clean_data[int(k)] = new_v
    return clean_data


def create_topology(key, num_nodes):
    """
    Based off of the passed in key and the number of nodes, returns a dictionary that
    keeps track of the mean latency between a set of nodes
    """
    topo = {}
    if key == "equadistant":
        for n1 in range(num_nodes):
            for n2 in range(n1+1, num_nodes):
                topo[(n1, n2)] = 200
    elif key == "wide-area":
        q1 = num_nodes//4
        q2 = 2*q1
        q3 = 3*q1
        for n1 in range(num_nodes):
            for n2 in range(num_nodes):
                if (n1 <= q1 and n2 <= q1) or (q1 < n1 <= q2 and q1 < n2 <= q2) or (q2 < n1 <= q3 and q2 < n2 <= q3) or (q3 < n1 <= num_nodes and q3 < n2 <= num_nodes):
                    topo[(n1, n2)] = 200
                else:
                    topo[(n1, n2)] = 400
    else:
        raise Exception(f"Invalid key: {key} does not exist!  Try using 'equadistant' or 'wide-area'")

    return topo
        

if __name__ == "__main__":
    if not args.name:
        raise Exception("Need to enter a valid name using the --name flag")

    # grabbing the pre-determined schedule
    with open(os.path.join("schedules", f"{args.schedule}.json")) as f:
        schedule = json.load(f)
        clean_schedule = clean_up_json(schedule)

    topo = create_topology(args.topo, args.nodes)

    # initialize the right network given the passed in type
    if args.type == "pow":
        net = ProofOfWorkNetwork([], exponential_latency(topo), clean_schedule)
    elif args.type == "c":
        net = CentralizedNetwork([], exponential_latency(topo), clean_schedule)
    elif args.type == "pos":
        net = ProofOfStakeNetwork([], exponential_latency(topo), clean_schedule)
    else:
        raise Exception(f"{args.type} is not a valid type")
    nodes = init_nodes(net, args.nodes)
    net.assign_nodes(nodes)

    # continues to increment time in the network until all transactions have been verfied across all nodes
    while True:
        res = net.tick()
        if res is not None:
            print("All transactions have been verified")
            latencies, consensus, computations, packets = res
            latencies["metrics"] = {"num_computations": computations, "num_packets": packets}

            os.mkdir(f"results/{args.name}-{args.type}-{args.topo}-{args.nodes}-nodes")
            with open(f"results/{args.name}-{args.type}-{args.topo}-{args.nodes}-nodes/results.json", 'w') as f:
                json.dump(latencies, f)
            break