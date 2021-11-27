import random

class Block:
    def __init__(self, block_id, data, timestamp, previous_hash=None):
        self.block_id = block_id
        self.data = data
        self.nonce = random.randint(0, 100000000)
        self.block_hash = None
        self.previous_hash = previous_hash
        self.next_hash = None
        self.next_block = None
        self.timestamp = timestamp
    
    def hash(self):
        res = f"{str(self.block_id)}{str(self.data)}{str(self.nonce)}{str(self.timestamp)}"
        return hash(res)
    
    def assign_nonce(self, value):
        self.nonce = value
    
    def assign_hash(self):
        self.block_hash = self.hash()