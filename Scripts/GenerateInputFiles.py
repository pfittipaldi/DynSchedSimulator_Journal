#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 11 09:18:24 2022

@author: root
"""

import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from numpy.random import default_rng
import itertools as it
from math import sqrt
from random import random
import Inputs_For_GenerateInputFiles as ui

def cast_route_to_string(route):
    StrRoute = ''
    for i in route:
        StrRoute = StrRoute + str(i)
    return StrRoute


rng = default_rng()
graph_is_connected = False
user_provided_graph = False

# Generating a connected graph with the specifications provided in the input file

if ui.Graph_Type == "C":
     G = ui.G
     user_provided_graph = True

while graph_is_connected == False and user_provided_graph == False:
    if ui.Graph_Type == "WS":
        G = nx.watts_strogatz_graph(ui.n_nodes,ui.n_neighbors,ui.p)
        pos = nx.shell_layout(G)
    elif ui.Graph_Type == "ER":
        G = nx.erdos_renyi_graph(ui.n_nodes, ui.p)
        pos = nx.shell_layout(G)
    elif ui.Graph_Type[-1] == "G": #IF THE GRAPH IS A GRID, NORMAL OR PROBABILISTIC:
        while sqrt(ui.n_nodes) != int(sqrt(ui.n_nodes)):
            ui.n_nodes = ui.n_nodes-1
        n = int(sqrt(ui.n_nodes))
        G = nx.grid_2d_graph(n,n)
        pos = dict((n, n) for n in G.nodes() ) #Dictionary of all positions, useful to keep the grid layout in the plots
        if ui.Graph_Type[0] == "p": # IF THE GRID IS PROBABILISTIC:
            to_iterate = G.copy().nodes()
            for node in to_iterate:
               if random() <= ui.p:
                   G.remove_node(node)
                   pos.pop(node)
    graph_is_connected = nx.is_connected(G)

# Renaming nodes
if len(G) > 52:
    print("The code currently supports graphs that have <= 52 nodes.")
    exit()

names = list("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")[0:len(G)]
G = nx.relabel_nodes(G, dict(zip(G.nodes,names)))



SPair1 = ui.SPair1
SPair2 = ui.SPair2

if SPair1 is None or SPair2 is None:
    plt.figure()
    if pos != dict():
        pos = dict(zip(G.nodes,pos.values())) # Take the old positions and give them to the new nodes
        nx.draw(G, with_labels=True,pos=pos)
    else:
        nx.draw(G, with_labels=True)

    plt.show()
    if SPair1 is None:
        SPair1 = tuple(input("Insert the first service pair:"))
    if SPair2 is None:
        SPair2 = tuple(input("Insert the second service pair:"))

Load_Points = np.linspace(0,ui.Max_Ppairs_Load,ui.N_Load_Points)

with open("Scripts/Simulation_Parameters.py") as f:
    Unchanging_inputs = f.read()

for conf in range(ui.Configs_toGen): 
    rSPair1 = tuple(reversed(SPair1))
    rSPair2 = tuple(reversed(SPair2))
    
    
    if ui.IncludePhysicalQueues:
        DrawPool = set(it.combinations(G.nodes,2)) - set(SPair1,SPair2,rSPair1,rSPair2)
    else:
        DrawPool = set(it.combinations(G.nodes,2)) - set(G.edges) - set((SPair1,SPair2,rSPair1,rSPair2))
    
    
    DrawPool = list(DrawPool) # Casting to list because rng.choice takes a list as input
    
    
    RAW_SPairs = list(rng.choice(DrawPool,ui.Num_Pairs-2))
    for i, _ in enumerate(RAW_SPairs):
        RAW_SPairs[i] = tuple(RAW_SPairs[i])
    
    
    RAW_SPairs = [SPair1, SPair2] + RAW_SPairs
    
    routes = []
    
    SPairs = RAW_SPairs
    
    for cutoff in range(1,ui.Num_Routes+1): # Find n routes for the pairs
        routes = []
        for pair in SPairs:
            newGraph = G.copy()
            for i in range(cutoff):
                if nx.has_path(newGraph,pair[0],pair[1]):
                    route = nx.shortest_path(newGraph, pair[0],pair[1]) #Find the route
                    StrRoute = cast_route_to_string(route)
                    routes.append(StrRoute)
                    for edge in nx.utils.pairwise(route):
                        if random() <= ui.path_pop_prob:
                            newGraph.remove_edge(edge[0],edge[1])
                            
        for ld in Load_Points:
            for policy in ui.policies_to_simulate:
                CompleteName = "Sim_inputs_C" + str(conf) + "_L" + str(int(ld/1000)) + "_" + policy["short_name"] + "_" + str(cutoff) + "routes.py"
                # OUTPUT
                with open(CompleteName,"w") as f:
                    f.write(Unchanging_inputs)
                    f.write("\n")
                    f.write("ArrRates = {\n")
                    end = len(G.edges)
                    for i in G.edges:
                        if i != end:
                            f.write(f"frozenset(('{i[0]}','{i[1]}')) : {ui.GenRate},\n")
                        else:
                            f.write(f"frozenset(('{i[0]}','{i[1]}')) : {ui.GenRate}\n")
                    f.write("}\n")
                    f.write(f"topologyname = \"{ui.Graph_Type}({ui.n_nodes},{ui.n_neighbors},{ui.p}), {ui.Num_Pairs}p\"\n")
                    f.write(f"routes = {routes}\n")
                    f.write(f"SPairs = {SPairs}\n")
                    f.write(f"DemRateRest = {int(ld)}\n")
                    f.write(f"policy = {policy}")



