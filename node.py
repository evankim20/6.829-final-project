

from util import generate_keys
from blockchain import Blockchain
from util import generate_keys

class Node:
    def __init__(self, id, net, genesis_block):
        self.id = id
        self.public_key, self.private_key = generate_keys()
        self.ledger = Blockchain(genesis_block)
        self.net = net

    def mine(self):
        return self.ledger.mine()

    def add_block(self, block):
        return self.ledger.add_block(block)

    def send_transaction(self, txn):
        self.net.add_transaction(txn)

    def tick(self):
        # mine for a new block
        new_block = self.mine()
        if new_block is not None:
            # propagate mined block to the network
            self.net.broadcast_block(new_block, self)