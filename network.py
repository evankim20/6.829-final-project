"""

"""

from constants import BLOCK, TRANSACTION

class Network:
    def __init__(self, nodes, latency_fn, schedule):
        self.nodes = nodes
        self.time = 0
        self.latency_fn = latency_fn
        self.latencies = {}
        self.incoming_messages = {} # maps from node id to a dictionary mapping times to (incoming data, type of packet)
        self.schedule = schedule
        self.transaction_num = 1

    def assign_nodes(self, nodes):
        self.nodes = nodes
        for n in self.nodes:
            self.incoming_messages[n.id] = {}

    def check_for_majority(self):
        most_recent_blocks = [n.ledger.genesis_block for n in self.nodes]
        exhaused_nodes = set([])
        most_recent_block = most_recent_blocks[0]
        majority = round(len(self.nodes)/2)
        while True:
            for i in range(len(self.nodes)):
                if i in exhaused_nodes:
                    continue
                next_block = most_recent_blocks[i].next_block
                if next_block is None:
                    exhaused_nodes.add(i)
                most_recent_blocks[i] = next_block
            # check if less than a majority has agreed upon an incoming block
            if len(self.nodes) - len(exhaused_nodes) < majority:
                return most_recent_block.block_id
            
            for i in range(len(self.nodes)):
                if i not in exhaused_nodes:
                    most_recent_block = most_recent_blocks[i]
                    break
    
    def calculate_latency(self, ind):
        for i in range(1, ind+1):
            if 'LATENCY' in self.latencies[i]:
                continue
            self.latencies[i]['LATENCY'] = self.time - self.latencies[i]['start']
        print(self.latencies)
    
    def add_transaciton(self, txn, sending_node_id):
        """
        Sends a new transaction to the blockchain ledger to all neighboring nodes in the network
        """
        for node in self.nodes:
            # don't need to send the sender the transaction it is sending out
            if sending_node_id == node.id:
                if self.time not in self.incoming_messages[node.id]:
                    self.incoming_messages[node.id][self.time] = []
                self.incoming_messages[node.id][self.time].append((txn, TRANSACTION))
                continue
            
            assert node.id in self.incoming_messages, f"node-{node.id} is not in the dictionary storing queues for nodes"
            delay = self.latency_fn()
            future_time = self.time + delay
            if future_time not in self.incoming_messages[node.id]:
                self.incoming_messages[node.id][future_time] = []
            # TODO: have a certain delay for each pair of hosts, see whats up 
            self.incoming_messages[node.id][future_time].append((txn, TRANSACTION))

    
    def broadcast_block(self, block, sending_node_id):
        """
        Broadcasts a verfied block to all nodes in the network
        """
        for node in self.nodes:
            # don't need to send the sender the block it verified
            if sending_node_id == node.id:
                continue

            assert node.id in self.incoming_messages, f"node-{node.id} is not in the dictionary storing queues for nodes"
            delay = self.latency_fn()
            future_time = self.time + delay
            if future_time not in self.incoming_messages[node.id]:
                self.incoming_messages[node.id][future_time] = []
            self.incoming_messages[node.id][future_time].append((block, BLOCK))

    def search_for_txns(self, node_id, timestamp):
        assert node_id in self.incoming_messages, f"node-{node_id} is not in the dictionary storing queues for nodes"
        # no incoming packets
        if self.time not in self.incoming_messages[node_id]:
            return []
        return self.incoming_messages[node_id][timestamp]

    def apply_actions(self):
        """
        Takes all actions in the passed in schedule for the current time and processees the action
        """
        if self.time in self.schedule:
            actions = self.schedule[self.time]
            for sender_id, data in actions:
                self.latencies[self.transaction_num] = {'start': self.time}
                self.transaction_num += 1
                self.add_transaciton(data, sender_id)

    def seperate_packets(self, packets):
        verified_blocks = []
        transactions = []
        for pkt, pkt_type in packets:
            if pkt_type == BLOCK:
                verified_blocks.append(pkt)
            if pkt_type == TRANSACTION:
                transactions.append(pkt)
        return verified_blocks, transactions

    def tick(self):
        ind = self.check_for_majority()
        # TODO: given conensus, calculate any latency values
        self.calculate_latency(ind)

        self.apply_actions()     

        for node in self.nodes:
            # node checks if it has any actions at this time (send txn or add block) -- incoming messages
            incoming_packets = self.search_for_txns(node.id, self.time)
            verified_blocks, transactions = self.seperate_packets(incoming_packets)
            for pkt in sorted(verified_blocks, key=lambda x: x.block_id):
                add_block_success = node.add_block(pkt)
                # assert add_block_success, f"failed to insert block for node-{node.id} {node.ledger.most_recent_block.data}, {pkt.data}"
            for pkt in transactions:
                   node.ledger.add_incoming_txn(pkt)
        
        for node in self.nodes:
            new_block = node.mine()
            if new_block is not None:
                print(f"{node.id} just mined a new block with id: ", new_block.block_id, f"prev data {node.ledger.most_recent_block.data} vs {new_block.data}")
                self.broadcast_block(new_block, node.id)

        self.time += 1

