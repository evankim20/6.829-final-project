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


def save_bar_graph():
    pow_data = json.load(open(f"results/{args.name}-pow-{args.topo}-{args.nodes}-nodes/results.json"))
    pos_data = json.load(open(f"results/{args.name}-pos-{args.topo}-{args.nodes}-nodes/results.json"))
    c_data = json.load(open(f"results/{args.name}-c-{args.topo}-{args.nodes}-nodes/results.json"))
    pow_av = average_latency(pow_data)
    pos_av = average_latency(pos_data)
    c_av = average_latency(c_data)
    data = {"Centralized" : c_av, "Proof of Work": pow_av, "Proof of Stake": pos_av}
    plt.bar(list(data.keys()), list(data.values()), color = 'red', width = 0.4)
    plt.xlabel("Type of Protocol")
    plt.ylabel("Average Latency")
    plt.title("Latency Depending on Protocol")
    utils.mkdir_if_not_exists(f"graphs/{args.name}-{args.topo}-{args.nodes}-nodes")
    plt.savefig(f"graphs/{args.name}-{args.topo}-{args.nodes}-nodes/figure.png")




def main():
    if args.type == "none":
        save_bar_graph()



if __name__ == "__main__":
    main()


