import numpy as np
import json
import os
import sys
import argparse
import matplotlib as mpl
import matplotlib.pyplot as plt
sys.path.append('./')
import utils

from argparse import ArgumentParser
parser = ArgumentParser(description="Script to generate graph")
parser.add_argument('--graph',
                    type=str,
                    help="What type of protocol to run (proof_of_work (pow), proof_of_stake (pos), or centralized (c)",
                    default="none")
parser.add_argument('--type',
                    type=str,
                    help="What type of protocol to run (proof_of_work (pow), proof_of_stake (pos), or centralized (c)",
                    default="none")
parser.add_argument('--nodes',
                    type=int,
                    help="Number of nodes to launch",
                    default=5)
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

def average_latency(j):
    total_lat = 0
    for key, val in j.items():
        if "LATENCY" in val:
            total_lat += val["LATENCY"]
    return total_lat / (len(j)-1)

def packets(j):
    return j["metrics"]["num_packets"]

def computations(j):
    return j["metrics"]["num_computations"]

def save_bar_graphs(pow_data, pos_data, c_data):
    if args.topo == "equadistant":
        topo = "Equadistant"
    else:
        topo = "Wide Area"
    pow_av = average_latency(pow_data)
    pos_av = average_latency(pos_data)
    c_av = average_latency(c_data)
    data = {"Centralized" : c_av, "Proof of Work": pow_av, "Proof of Stake": pos_av}
    plt.bar(list(data.keys()), list(data.values()), color = 'red', width = 0.4)
    plt.xlabel("Type of Protocol")
    plt.ylabel("Average Latency")
    plt.title("Latency Depending on Protocol for " + topo + " Topology")
    utils.mkdir_if_not_exists(f"graphs/{args.name}-{args.topo}-{args.nodes}-nodes")
    plt.savefig(f"graphs/{args.name}-{args.topo}-{args.nodes}-nodes/average_latencies.png")
    # packets
    plt.clf()
    data = {"Centralized" : computations(c_data), "Proof of Work": computations(pow_data), "Proof of Stake": computations(pos_data)}
    plt.bar(list(data.keys()), list(data.values()), color = 'green', width = 0.4)
    plt.xlabel("Type of Protocol")
    plt.ylabel("Number of Computations")
    plt.title("Computations Depending on Protocol for " + topo + " Topology")
    utils.mkdir_if_not_exists(f"graphs/{args.name}-{args.topo}-{args.nodes}-nodes")
    plt.savefig(f"graphs/{args.name}-{args.topo}-{args.nodes}-nodes/total_computations.png")
    # packets
    plt.clf()
    data = {"Centralized" : packets(c_data), "Proof of Work": packets(pow_data), "Proof of Stake": packets(pos_data)}
    plt.bar(list(data.keys()), list(data.values()), color = 'green', width = 0.4)
    plt.xlabel("Type of Protocol")
    plt.ylabel("Number of Packets")
    plt.title("Packets Depending on Protocol for " + topo + " Topology")
    utils.mkdir_if_not_exists(f"graphs/{args.name}-{args.topo}-{args.nodes}-nodes")
    plt.savefig(f"graphs/{args.name}-{args.topo}-{args.nodes}-nodes/total_packets.png")
    # packets / latency
    plt.clf()
    data = {"Centralized" : packets(c_data) / average_latency(c_data), "Proof of Work": packets(pow_data) / average_latency(pow_data), "Proof of Stake": packets(pos_data) / average_latency(pos_data)}
    plt.bar(list(data.keys()), list(data.values()), color = 'green', width = 0.4)
    plt.xlabel("Type of Protocol")
    plt.ylabel("Packets / Latency")
    plt.title("Throughput Depending on Protocol for " + topo + " Topology")
    utils.mkdir_if_not_exists(f"graphs/{args.name}-{args.topo}-{args.nodes}-nodes")
    plt.savefig(f"graphs/{args.name}-{args.topo}-{args.nodes}-nodes/packets_over_latency.png")


def save_line_graph(pow_data, pos_data, c_data):
    if args.topo == "equadistant":
        topo = "Equadistant"
    else:
        topo = "Wide Area"
    start_time_arrays = []
    latency_arrays = []
    for data in [pow_data, pos_data, c_data]:
        start_times = []
        latencies = []
        for key, val in data.items():
            if "LATENCY" in val:
                start_times.append(val["start"])
                latencies.append(val["LATENCY"])
        start_time_arrays.append(start_times)
        latency_arrays.append(latencies)
    for i in range(3):
        if i == 0:
            label = "Proof of Work"
        elif i == 1:
            label = "Proof of Stake"
        else:
            label = "Centralized"
        plt.plot(start_time_arrays[i], latency_arrays[i], label=label)
        plt.legend()
    plt.xlabel("Start Times")
    plt.ylabel("Latency")
    plt.title("Latencies Over Time for " + topo + " Topology")
    plt.savefig(f"graphs/{args.name}-{args.topo}-{args.nodes}-nodes/latency_over_time.png")

def save_line_graphs():
    nodes = [3, 5, 10, 25, 50, 100, 250, 500, 1000]
    protocols = ["c", "pos", "pow"]
    for protocol in protocols:
        computations_array = []
        for node in nodes:
            data = json.load(open(f"results/{args.name}-{protocol}-{args.topo}-{node}-nodes/results.json"))
            computations_array.append(computations(data))
        if protocol == "c":
            label = "Centralized"
        elif protocol == "pos":
            label = "Proof of Stake"
        else:
            label = "Proof of Work"
        plt.plot(nodes, computations_array, label=label)
        plt.legend()
    plt.xlabel("# of Nodes")
    plt.ylabel("Computations")
    plt.title("# of Computations Based on Nodes")
    plt.savefig(f"graphs/computations_over_nodes.png")
    plt.clf()
    # packets
    for protocol in protocols:
        packets_array = []
        for node in nodes:
            data = json.load(open(f"results/{args.name}-{protocol}-{args.topo}-{node}-nodes/results.json"))
            packets_array.append(packets(data))
        if protocol == "c":
            label = "Centralized"
        elif protocol == "pos":
            label = "Proof of Stake"
        else:
            label = "Proof of Work"
        plt.plot(nodes, packets_array, label=label)
        plt.legend()
    plt.xlabel("# of Nodes")
    plt.ylabel("Packets")
    plt.title("# of Packets Based on Nodes")
    plt.savefig(f"graphs/packets_over_nodes.png")
    plt.clf()


def main():
    if args.graph == "none":
        pow_data = json.load(open(f"results/{args.name}-pow-{args.topo}-{args.nodes}-nodes/results.json"))
        pos_data = json.load(open(f"results/{args.name}-pos-{args.topo}-{args.nodes}-nodes/results.json"))
        c_data = json.load(open(f"results/{args.name}-c-{args.topo}-{args.nodes}-nodes/results.json"))
        save_bar_graphs(pow_data, pos_data, c_data)
        plt.clf()
        save_line_graph(pow_data, pos_data, c_data)
    else:
        save_line_graphs()



if __name__ == "__main__":
    main()


