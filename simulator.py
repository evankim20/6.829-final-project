from block import Block
from network import Network
from node import Node
from util import exponential_latency

import time

def init_nodes(net, n=3): 
    genesis_block = Block(block_id=0, data="genesis block", timestamp=time.time())
    nodes = []
    for i in range(n):
        nodes.append(Node(i, net, genesis_block))
    return nodes

if __name__ == "__main__":
    # TODO: flags for  time, num nodes, latency, etc...
    # LOG_DIR = "plot"
    # if not os.path.exists(LOG_DIR):
    #     os.makedirs(LOG_DIR)

    net = Network([], exponential_latency(25), {2: [(0, "first txn")], 100: [(2, "hi")], 200: [(4, "whatsup")]}) # TODO: arg shit
    nodes = init_nodes(net, 50) # TODO: args shit
    net.assign_nodes(nodes)

    # configuration = text file load of all transactions that are trying to take place and latencies

    while True:
        net.tick()