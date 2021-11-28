import time

from block import Block


class Blockchain:
    """
    Data structure that stores the chain of blocks and performs computations to add new blocks and perform the proof of work
    """
    def __init__(self, genesis_block):
        # initialize the genesis block
        self.genesis_block = genesis_block
        self.genesis_block.assign_hash()
        self.most_recent_block = self.genesis_block
        self.unconfirmed_txns = []
        self.previous_data = set([genesis_block.data])
        self.current_nonce = 0
        self.current_num_computations = 0
    
    def _same_hash(self, last_block, new_block):
        """
        confirms that the new block correclty assigned their previous hash to be the hash of the block
        preceding it
        """
        return last_block.block_hash == new_block.previous_hash
    
    def _validate_proof(self, block):
        """
        Confirms that the block's hash is consistent with the hash generated
        """
        return block.block_hash == block.hash()

    def add_block(self, block):
        """
        Adds a new block to the blockchain
        """
        # we have already processes this block so we can ignore the incoming request
        if block.block_id <= self.most_recent_block.block_id:
            return True
        # the new block doesn't pass the validation 
        if not self._same_hash(self.most_recent_block, block) or not self._validate_proof(block):
            return False
        # assigning the new block to the chain and updating pointers
        self.most_recent_block.next_hash = block.hash
        self.most_recent_block.next_block = block
        self.most_recent_block = block
        self.previous_data.add(block.data)
        return True
    
    def add_block_centralized(self, block):
        """
        For the centralized architecture, accept a block and don't do any verfication since the 
        centralized server is trusted
        """
        if block.data in self.previous_data:
            return True
        self.most_recent_block.next_block = block
        self.most_recent_block = block
        self.previous_data.add(block.data)
        return True

    def add_incoming_txn(self, block):
        """
        Place a new block into this Chain's uncofirmed transactions
        """
        self.unconfirmed_txns.append(block)

    def proof_of_work(self, block):
        """
        Apply the proof of work computation by updating the nonce value and checking if the hash of the block
        is divisible by 600
        """
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
        """
        For the centralized architecture, immediatley create a new block without mining the block
        """
        prev_block = self.most_recent_block
        next_block_id = prev_block.block_id + 1
        new_block = Block(block_id=next_block_id, data=pkt, timestamp=time.time())
        return new_block

    def mine(self):
        """
        Perform the mining computation of working on an incoming transaction, finding the nonce, and calcuating the proof
        if the nonce value solves the problem.
        """
        # no incoming transactions to mine
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
        # new block
        next_block = Block(block_id=next_block_id, data=next_block_data, timestamp=time.time(), previous_hash=prev_block.block_hash)
        # calculate nonce and hash value
        proof, num_computations = self.proof_of_work(next_block)
        # haven't found the correct nonce this round
        if proof is None:
            return None

        # successfully found the nonce 
        if next_block.data not in self.previous_data:
            # add to current Blockchain the newly mined block
            self.add_block(next_block)
        # remove the transaction from the list since we solved it
        self.unconfirmed_txns.pop(0)
        return next_block, num_computations