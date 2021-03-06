"""
Contains the parent class and the subclasses that represent the different architectures (Cenralized, PoW, PoS)
"""

from constants import BLOCK, TRANSACTION

import random
import numpy as np


class Network:
    """
    Parent class for all of the networks
    """
    def __init__(self, nodes, latency_fn, schedule):
        self.nodes = nodes
        self.time = 0
        self.latency_fn = latency_fn 
        self.latencies = {} # maps from block id to time it took to get a majority consensus
        self.consensus_times = {} # maps from block id to time it took to get consensus among all nodes
        self.incoming_messages = {} # maps from node id to a dictionary mapping times to (incoming data, type of packet)
        self.schedule = schedule # maps the time and the list of transactions that will happen at that time
        self.last_block_id = len(schedule) # TODO: this isn't true when we have multiple txn in a block
        self.transaction_num = 1
        self.packets_sent = 0
        self.num_computations = 0
        self.in_transit = {}

    def assign_nodes(self, nodes):
        """
        Updates the nodes in the network
        """
        self.nodes = nodes
        for n in self.nodes:
            self.incoming_messages[n.id] = {}

    def check_for_majority(self):
        """
        Looks over all nodes and checks to see which block index is agreed upon by the majority of nodes
        """
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
    
    def check_for_consensus(self):
        """
        Looks over all nodes and checks to see which block index is agreed upon amongst all nodes
        """
        most_recent_blocks = [n.ledger.genesis_block for n in self.nodes]
        most_recent_block = most_recent_blocks[0]
        while True:
            for i in range(len(self.nodes)):
                next_block = most_recent_blocks[i].next_block
                if next_block is None:
                    return most_recent_block.block_id
                most_recent_blocks[i] = next_block
            most_recent_block = most_recent_blocks[0]
    
    def calculate_latency(self, ind):
        """
        Checks which blocks are verified, and calculates the latency for these blocks
        """
        for i in range(1, ind+1):
            if 'LATENCY' in self.latencies[i]:
                continue
            self.latencies[i]['LATENCY'] = self.time - self.latencies[i]['start']
        # print("LATENCIES", self.latencies, self.time)
    
    def calculate_consensus(self, ind):
        """
        Checks which blocks are verified and agreed upon by all nodes, and calculates the latency for these blocks
        """
        for i in range(1, ind+1):
            if 'LATENCY' in self.consensus_times[i]:
                continue
            self.consensus_times[i]['LATENCY'] = self.time - self.consensus_times[i]['start']

    def search_for_txns(self, node_id, timestamp):
        """
        Look for incoming messages for the given node at the current time
        """
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
                # initialze latency and consensus dictionaries for the block
                self.latencies[self.transaction_num] = {'start': self.time}
                self.consensus_times[self.transaction_num] = {'start': self.time}
                self.transaction_num += 1
                self.add_transaction(data, sender_id)

    def seperate_packets(self, packets):
        """
        Takes a list of incoming packets and seperates the packets by those that are verified blocks vs
        incoming transactions
        """
        verified_blocks = []
        transactions = []
        for pkt, pkt_type, sender_id in packets:
            if pkt_type == BLOCK:
                verified_blocks.append((pkt, sender_id))
            if pkt_type == TRANSACTION:
                transactions.append((pkt, sender_id))
        return verified_blocks, transactions

    def broadcast_block(self, block, sending_node_id):
        """
        Broadcasts a verfied block to all nodes in the network
        """
        for node in self.nodes:
            # don't need to send the sender the block it verified
            if sending_node_id == node.id:
                continue

            assert node.id in self.incoming_messages, f"node-{node.id} is not in the dictionary storing queues for nodes"
            delay = self.latency_fn(sending_node_id, node.id)
            additional_delay = self.get_additional_delay(sending_node_id, node.id)
            future_time = self.time + delay
            if future_time not in self.incoming_messages[node.id]:
                self.incoming_messages[node.id][future_time] = []
            self.incoming_messages[node.id][future_time].append((block, BLOCK, sending_node_id))
            self.packets_sent += 1

    def get_additional_delay(self, sending_id, recieving_id):
        if sending_id == recieving_id:
            return 0
        
        if (sending_id, recieving_id) in self.in_transit:
            count = self.in_transit[(sending_id, recieving_id)]
            self.in_transit[(sending_id, recieving_id)] += 1
            return np.random.poisson(2**count)

        self.in_transit[(sending_id, recieving_id)] = 1
        return 0

    def remove_from_transit(self, sending_id, recieving_id):
        if sending_id == recieving_id:
            return

        if (sending_id, recieving_id) in self.in_transit and self.in_transit[(sending_id, recieving_id)] > 0:
            self.in_transit[(sending_id, recieving_id)] -= 1

    
class CentralizedNetwork(Network):
    """
    Centralized architecture where the first node is the centralized server that handles transactions
    """
    def __init__(self, nodes, latency_fn, schedule):
        super().__init__(nodes, latency_fn, schedule)
    
    def assign_nodes(self, nodes):
        self.nodes = nodes
        for n in self.nodes:
            self.incoming_messages[n.id] = {}
        # set centralized server to be the first node
        self.centralized_server = self.nodes[0]

    def add_transaction(self, txn, sending_node_id):
        """
        Sends a new transaction to the centralized server to process
        """
        delay = self.latency_fn(sending_node_id, self.centralized_server.id)
        additional_delay = self.get_additional_delay(sending_node_id, self.centralized_server.id)
        future_time = self.time + delay + additional_delay
        if future_time not in self.incoming_messages[self.centralized_server.id]:
            self.incoming_messages[self.centralized_server.id][future_time] = []
        self.incoming_messages[self.centralized_server.id][future_time].append((txn, TRANSACTION, sending_node_id))
        self.packets_sent += 1
    
    def tick(self):
        """
        Runs computations on each node for one "time" tick
        """
        ind = self.check_for_majority()
        consensus_ind = self.check_for_consensus()
        self.calculate_latency(ind)
        self.calculate_consensus(consensus_ind)
        
        # termination condition
        if consensus_ind == self.last_block_id:
            print(f"Latencies: {self.latencies}\nConsensus: {self.consensus_times}\nNumber of Computations: {self.num_computations}\nPackets Sent {self.packets_sent}")
            return self.latencies, self.consensus_times, self.num_computations, self.packets_sent

        self.apply_actions()     

        for node in self.nodes:
            # node checks if it has any actions at this time (send txn or add block) -- incoming messages
            incoming_packets = self.search_for_txns(node.id, self.time)
            verified_blocks, transactions = self.seperate_packets(incoming_packets)
            # handle the verified blocks first
            for pkt, sender_id in sorted(verified_blocks, key=lambda x: x[0].block_id):
                node.add_block_centralized(pkt)
                self.remove_from_transit(sender_id, node.id)
            for pkt, sender_id in transactions:
                new_block = node.ledger.process_txn(pkt)
                node.add_block_centralized(new_block)
                self.broadcast_block(new_block, node.id)
                self.remove_from_transit(sender_id, node.id)
        self.time += 1


class ProofOfWorkNetwork(Network):
    """
    Proof of Work architecture
    """
    def __init__(self, nodes, latency_fn, schedule):
        super().__init__(nodes, latency_fn, schedule)
    
    def add_transaction(self, txn, sending_node_id):
        """
        Sends a new transaction to the blockchain ledger to all neighboring nodes in the network
        """
        for node in self.nodes:
            # don't need to send the sender the transaction it is sending out
            if sending_node_id == node.id:
                if self.time not in self.incoming_messages[node.id]:
                    self.incoming_messages[node.id][self.time] = []
                self.incoming_messages[node.id][self.time].append((txn, TRANSACTION, sending_node_id))
                continue
            
            assert node.id in self.incoming_messages, f"node-{node.id} is not in the dictionary storing queues for nodes"
            delay = self.latency_fn(sending_node_id, node.id)
            additional_delay = self.get_additional_delay(sending_node_id, node.id)
            future_time = self.time + delay +additional_delay
            if future_time not in self.incoming_messages[node.id]:
                self.incoming_messages[node.id][future_time] = []
            self.incoming_messages[node.id][future_time].append((txn, TRANSACTION, sending_node_id))
            self.packets_sent += 1

    def tick(self):
        """
        Runs computations on each node for one "time" tick
        """
        print(self.in_transit)
        ind = self.check_for_majority()
        consensus_ind = self.check_for_consensus()
        self.calculate_latency(ind)
        self.calculate_consensus(consensus_ind)

        # termination condition
        if consensus_ind == self.last_block_id:
            print(f"Latencies: {self.latencies}\nConsensus: {self.consensus_times}\nNumber of Computations: {self.num_computations}\nPackets Sent {self.packets_sent}")
            return self.latencies, self.consensus_times, self.num_computations, self.packets_sent

        self.apply_actions()     

        for node in self.nodes:
            # node checks if it has any actions at this time (send txn or add block) -- incoming messages
            incoming_packets = self.search_for_txns(node.id, self.time)
            verified_blocks, transactions = self.seperate_packets(incoming_packets)
            for pkt, sender_id in sorted(verified_blocks, key=lambda x: x[0].block_id):
                node.add_block(pkt)
                self.remove_from_transit(sender_id, node.id)
            for pkt, sender_id in transactions:
                node.ledger.add_incoming_txn(pkt)
                self.remove_from_transit(sender_id, node.id)
        
        # perform mining on each node
        for node in self.nodes:
            res = node.mine()

            # if we have found a solution
            if res is not None:
                new_block, num_computations = res
                self.num_computations += num_computations
                # notify neighbors of the new block mined
                self.broadcast_block(new_block, node.id)
        self.time += 1

class ProofOfStakeNetwork(Network):
    """
    Proof of Stake architecture
    """
    def __init__(self, nodes, latency_fn, schedule):
        super().__init__(nodes, latency_fn, schedule)

    def assign_nodes(self, nodes):
        self.nodes = nodes
        for n in self.nodes:
            self.incoming_messages[n.id] = {}
        # randomly assign validator node
        self.validator_node_id = random.randint(0, len(self.nodes)-1)

    def add_transaction(self, txn, sending_node_id):
        """
        Sends a new transaction to the validator node
        """
        validator_node = self.nodes[self.validator_node_id]
        # don't need to send the sender the transaction it is sending out
        if sending_node_id == validator_node.id:
            if self.time not in self.incoming_messages[validator_node.id]:
                self.incoming_messages[validator_node.id][self.time] = []
            self.incoming_messages[validator_node.id][self.time].append((txn, TRANSACTION, sending_node_id))
            return
        
        # sending to validator node
        assert validator_node.id in self.incoming_messages, f"node-{validator_node.id} is not in the dictionary storing queues for nodes"
        delay = self.latency_fn(sending_node_id, self.validator_node_id)
        additional_delay = self.get_additional_delay(sending_node_id, self.validator_node_id)
        future_time = self.time + delay + additional_delay
        if future_time not in self.incoming_messages[validator_node.id]:
            self.incoming_messages[validator_node.id][future_time] = []
        self.incoming_messages[validator_node.id][future_time].append((txn, TRANSACTION, sending_node_id))
        self.packets_sent += 1
        # # reasseign validator node
        # self.validator_node_id = random.randint(0, len(self.nodes) -1)

    def tick(self):
        """
        Runs computations on each node for one "time" tick
        """
        ind = self.check_for_majority()
        consensus_ind = self.check_for_consensus()
        self.calculate_latency(ind)
        self.calculate_consensus(consensus_ind)

        # termination condition
        if consensus_ind == self.last_block_id:
            print(f"Latencies: {self.latencies}\nConsensus: {self.consensus_times}\nNumber of Computations: {self.num_computations}\nPackets Sent {self.packets_sent}")
            return self.latencies, self.consensus_times, self.num_computations, self.packets_sent

        self.apply_actions()     

        for node in self.nodes:
            # node checks if it has any actions at this time (send txn or add block) -- incoming messages
            incoming_packets = self.search_for_txns(node.id, self.time)
            verified_blocks, transactions = self.seperate_packets(incoming_packets)
            for pkt, sender_id in sorted(verified_blocks, key=lambda x: x[0].block_id):
                node.add_block(pkt)
                self.remove_from_transit(sender_id, node.id)
            for pkt, sender_id in transactions:
                node.ledger.add_incoming_txn(pkt)
                self.remove_from_transit(sender_id, node.id)
        
        # validator node needs to mine block if there are awaiting transactions
        validator_node = self.nodes[self.validator_node_id]
        res = validator_node.mine_pos()
        # successful mined block
        if res is not None:
            new_block, num_computations = res
            self.num_computations += num_computations
            self.broadcast_block(new_block, self.validator_node_id)
        self.time += 1 