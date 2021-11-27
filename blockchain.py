from block import Block

import time
import random

class Blockchain:
    """
    
    """
    def __init__(self, genesis_block):
        self.genesis_block = genesis_block
        self.genesis_block.assign_hash()
        self.most_recent_block = self.genesis_block
        self.unconfirmed_txns = []
        self.previous_data = set([genesis_block.data])
        self.current_nonce = 0
        self.current_num_computations = 0
    
    def _same_hash(self, last_block, new_block):
        print(last_block.block_hash, new_block.previous_hash)
        return last_block.block_hash == new_block.previous_hash
    
    def _validate_proof(self, block):
        return block.block_hash == block.hash()

    def add_block(self, block):
        if block.block_id <= self.most_recent_block.block_id:
            return True
        if not self._same_hash(self.most_recent_block, block) or not self._validate_proof(block):
            print("FAIL", self.most_recent_block.block_id, block.block_id, self.most_recent_block.data, block.data)
            return False
        self.most_recent_block.next_hash = block.hash
        self.most_recent_block.next_block = block
        self.most_recent_block = block
        self.previous_data.add(block.data)
        return True
    
    def add_block_centralized(self, block):
        self.most_recent_block.next_block = block
        self.most_recent_block = block
        self.previous_data.add(block.data)
        return True

    def add_incoming_txn(self, block):
        self.unconfirmed_txns.append(block)

    def proof_of_work(self, block):
        self.current_nonce += 1
        self.current_num_computations += 1
        block.assign_nonce(self.current_nonce)
        h = block.hash()
        if h % 600 == 0:
            block.assign_hash()
            num_computations = self.current_num_computations
            self.current_num_computations = 0
            return h, num_computations
        return None, -1

    def process_txn(self, pkt):
        prev_block = self.most_recent_block
        next_block_id = prev_block.block_id + 1
        new_block = Block(block_id=next_block_id, data=pkt, timestamp=time.time())
        return new_block

    def mine(self):
        if not self.unconfirmed_txns:
            return None
        prev_block = self.most_recent_block
        next_block_id = prev_block.block_id + 1
        next_block_data = self.unconfirmed_txns[0]
        # stop working on mining a block if it has already been mined
        while next_block_data in self.previous_data:
            self.unconfirmed_txns.pop(0)
            if len(self.unconfirmed_txns) == 0:
                return None
            next_block_data = self.unconfirmed_txns[0]
        next_block = Block(block_id=next_block_id, data=next_block_data, timestamp=time.time(), previous_hash=prev_block.block_hash)

        proof, num_computations = self.proof_of_work(next_block)
        # haven't found the correct nonce this round
        if proof is None:
            return None

        # successfully found the nonce 
        print("AFTER MINING")
        if next_block.data not in self.previous_data:
            self.add_block(next_block)
        # remove the transaction from the list
        self.unconfirmed_txns.pop(0)
        return next_block, num_computations