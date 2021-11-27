from block import Block
from network import CentralizedNetwork, ProofOfStakeNetwork, ProofOfWorkNetwork
from node import Node
from util import exponential_latency

from argparse import ArgumentParser
import json
import os
import time

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
# TODO: add argument about file to grab values from for latency matrix
args = parser.parse_args()


def init_nodes(net, n=3): 
    genesis_block = Block(block_id=0, data="genesis block", timestamp=time.time())
    nodes = []
    for i in range(n):
        nodes.append(Node(i, net, genesis_block))
    return nodes

def clean_up_json(data):
    clean_data = {}
    for k, v in data.items():
        new_v = []
        for timestamp, txn_data in v:
            new_v.append((int(timestamp), txn_data))
        clean_data[int(k)] = new_v
    return clean_data
        

if __name__ == "__main__":
    # TODO: flags for  time, num nodes, latency, etc...
    # LOG_DIR = "plot"
    # if not os.path.exists(LOG_DIR):
    #     os.makedirs(LOG_DIR)

    # TODO: grab schedule -- make sure to convert everything to int etc.
    print(os.path.join("schedules", f"{args.schedule}.json"))
    with open(os.path.join("schedules", f"{args.schedule}.json")) as f:
        schedule = json.load(f)
        clean_schedule = clean_up_json(schedule)

    print(clean_schedule)

    if args.type == "pow":
        net = ProofOfWorkNetwork([], exponential_latency(25), clean_schedule)
    elif args.type == "c":
        net = CentralizedNetwork([], exponential_latency(25), clean_schedule)
    elif args.type == "pos":
        net = ProofOfStakeNetwork([], exponential_latency(25), clean_schedule)
    else:
        raise Exception(f"{args.type} is not a valid type")
    nodes = init_nodes(net, args.nodes) # TODO: args shit
    net.assign_nodes(nodes)

    # configuration = text file load of all transactions that are trying to take place and latencies

    while True:
        net.tick()