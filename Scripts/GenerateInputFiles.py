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
from random import random, choice
import Inputs_For_GenerateInputFiles as ui

def cast_route_to_string(route):
    StrRoute = ''
    for i in route:
        StrRoute = StrRoute + str(i)
    return StrRoute

def append_routes(pair,target_list):
    newGraph = G.copy()
    for i in range(cutoff):
        if nx.has_path(newGraph,pair[0],pair[1]):
            route = nx.shortest_path(newGraph, pair[0],pair[1]) #Find the route
            StrRoute = cast_route_to_string(route)
            if StrRoute not in target_list:
                target_list.append(StrRoute) 
                for edge in nx.utils.pairwise(route):
                    if random() <= ui.path_pop_prob:
                        newGraph.remove_edge(edge[0],edge[1])
                if newGraph.edges() == G.edges(): # If no edge has been removed, remove one at random. 
                    edge = choice(list(nx.utils.pairwise(route)))
                    newGraph.remove_edge(edge[0],edge[1]) 

def increase_pair_occurrencies(pair,sizedict):
    for nd in pair:
        sizedict[nd] += 1


rng = default_rng()
graph_is_connected = False
user_provided_graph = False

# Generating a connected graph with the specifications provided in the input file

if ui.Graph_Type == "C":
     G = ui.G
     user_provided_graph = True
     pos = nx.shell_layout(G)
     
while not graph_is_connected and not user_provided_graph:
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
        pos = dict((n, np.array(n)) for n in G.nodes()) #Dictionary of all positions, useful to keep the grid layout in the plots
        
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

if (SPair1 is None or SPair2 is None) and ui.AutoSelectPairs == False:
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
elif ui.AutoSelectPairs == True:
     allpathslen = dict(nx.shortest_path_length(G)) # crawl the whole graph for longest paths
     candidate_spairs_dict = dict()
 
     for ls in allpathslen:
        to_crawl = allpathslen[ls]
        dest = max(to_crawl, key= lambda x : to_crawl.get(x))
        pathlen = allpathslen[ls][dest]
        candidate_spairs_dict[(ls,dest)] = (pathlen)
 
     SPair1 = max(candidate_spairs_dict,key = lambda x : candidate_spairs_dict.get(x))
 
     candidate_spairs_dict.pop(SPair1)
     if tuple(reversed(SPair1)) in candidate_spairs_dict:
         candidate_spairs_dict.pop(tuple(reversed(SPair1)))
 
     for pt in candidate_spairs_dict:
         if set(SPair1).intersection(set(pt)) != set():
             candidate_spairs_dict[pt] = 0
     
     SPair2 = max(candidate_spairs_dict,key = lambda x : candidate_spairs_dict.get(x))

Load_Points = np.linspace(0,ui.Max_Ppairs_Load,ui.N_Load_Points)

with open("Scripts/Simulation_Parameters.py") as f:
    Unchanging_inputs = f.read()

    rSPair1 = tuple(reversed(SPair1))
    rSPair2 = tuple(reversed(SPair2))

## Routing the main pairs outside the loop on Configs_toGen to keep them the same across draws:
    
for cutoff in range(1,ui.Num_Routes+1): # Generate 1route, 2routes, 3routes...Nroutes input files.
    sizeDict = dict(zip(G.nodes,[1]*len(G)))
    MainPairRoutes = []
    for pair in (SPair1,SPair2):
        append_routes(pair,MainPairRoutes) # This function already finds [cutoff] many routes!


    for conf in range(ui.Configs_toGen): 
        if ui.IncludePhysicalQueues:
            DrawPool = set(it.combinations(G.nodes,2)) - set(SPair1,SPair2,rSPair1,rSPair2)
        else:
            DrawPool = set(it.combinations(G.nodes,2)) - set(G.edges) - set((SPair1,SPair2,rSPair1,rSPair2))
        
        
        DrawPool = list(DrawPool) # Casting to list because rng.choice takes a list as input
        
        
        RAW_SPairs = list(rng.choice(DrawPool,ui.Num_Pairs-2))
        for i, _ in enumerate(RAW_SPairs):
            RAW_SPairs[i] = tuple(RAW_SPairs[i])
        
        for pair in RAW_SPairs:
            increase_pair_occurrencies(pair,sizeDict)
        
        RAW_SPairs = [SPair1, SPair2] + RAW_SPairs
        
        SPairs = RAW_SPairs
        
        
        routes = MainPairRoutes.copy()
        for pair in SPairs[2:]: # Route parasitic pairs
            append_routes(pair,routes)
                                
            for ld in Load_Points: # Print final file
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
    
    # Print a picture of the topology:
    inPair1 = lambda node : node in SPairs[0] 
    inPair2 = lambda node : node in SPairs[1]  
    inBoth =  lambda node : inPair1(node) and inPair2(node)
    inParasitic = lambda node : any(node in pr for pr in SPairs[2:])
    
    node_color_map = ['fuchsia' if inBoth(node) else 'blue' if inPair1(node) else 'red' if inPair2(node) else "limegreen" if inParasitic(node) else "grey" for node in G]  
    edge_color_map = []
    
    routespair1 = MainPairRoutes[:len(MainPairRoutes)//2]
    routespair2 = MainPairRoutes[len(MainPairRoutes)//2:]
    
    for rlist in (routespair1,routespair2):
        revroutes = []
        for rt in rlist:
            revroutes.append(rt[::-1])
        rlist += revroutes
    
    for edge in G.edges:
         if any([edge in nx.utils.pairwise(i) for i in routespair1]) and any([edge in nx.utils.pairwise(i) for i in routespair2]):
             edge_color_map.append("fuchsia")
         elif any([edge in nx.utils.pairwise(i) for i in routespair1]):
             edge_color_map.append("blue")
         elif any([edge in nx.utils.pairwise(i) for i in routespair2]):
             edge_color_map.append("red")
         else:
             edge_color_map.append("grey")
    
    if pos != dict():
        pos = dict(zip(G.nodes,pos.values())) # Take the old positions and give them to the new nodes
    else:
        pos = nx.shell_layout(G)
    
    
    #nx.draw(G,pos=pos,with_labels=True,node_color=node_color_map,edge_color=edge_color_map,width=2)
    plt.figure(cutoff)
    nx.draw(G,pos=nx.nx_agraph.graphviz_layout(G,prog="dot"),with_labels=True,node_color=node_color_map,edge_color=edge_color_map,width=2) 
    ax = plt.gca()
    ax.set_aspect("equal","box")
    plt.savefig(f"TOPO_{ui.Graph_Type}_{cutoff}routes.pdf",bbox_inches="tight")


# shift = 0.12
# if ui.Graph_Type[-1] == "G":
#     shifted_pos = {node: node_pos + 1.4*shift for node, node_pos in pos.items()}
# else:
#     shifted_pos = {node: node_pos + [shift*coord for coord in pos[node]] for node, node_pos in pos.items()}

# # Just some text to print in addition to node ids
# labels = sizeDict
# plt.figure(cutoff)
# nx.draw_networkx_labels(G, shifted_pos, labels=labels, horizontalalignment="center")



