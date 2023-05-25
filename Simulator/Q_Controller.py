#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 19 12:36:18 2023

@author: paolo
This class mimics the classical control layer. It receives signals from the Simulation Kernel and relays them to the relevant nodes. 
"""
from numpy.random import default_rng
from Q_Node import Q_Node
from SchedulingModule import SchedulingModule
import User_Input as ui
import numpy as np


class Q_Controller:
    def __init__(self,G,Links_dict,rank,Rs_Labels,Ms,Ns):
        self.rng = default_rng()
        self.memo_archive = self.boot_cache() # Memoization archive, shared by all schedulers attached to this controller.
        self.links_dict = Links_dict
        self.nodes_dict=dict()
        self.rank = rank
        self.MaxRank = max(rank.keys())
        self.Rs_Labels = Rs_Labels
        self.Ms = Ms
        self.Ns = Ns
        self.node_order = None
        self.discover_links()
        self.boot_nodes()
        self.node_order = list(self.nodes_dict.keys())
        
        
        if ui.policy["localization"] == "Global":
            self.scheduler = SchedulingModule(Ms,Ns,self.memo_archive)
    
    def boot_cache(self):
        try:
            cache = np.load("controller_cache.npy",allow_pickle=True)
            cache = cache.item(0)
            #print("Successfully loaded on-disk cache! (delete the controller_cache.npy file if you want a cold-start)")
        except FileNotFoundError:
             cache = dict()
        return cache
    
    def getArchive(self):
        return self.memo_archive
    
    def boot_nodes(self):
        for link in self.links_dict:
            for node in link:
                self.connect_node(node)
                self.getNode(node).connect_queue(self.links_dict[link])
             
    
    def discover_links(self):
        average_info_raw=[] # alpha, beta and eta for all links. 
        for link in self.links_dict:
            average_info_raw.append(self.getLink(link).getAverages())
        average_info_raw = list(zip(*average_info_raw))
        self.average_info = dict(zip(["alpha","beta","eta"],average_info_raw))
        
    def getLink(self,link):
        return self.links_dict[link]
    
    def connect_node(self,node):
        if node not in self.nodes_dict:
            self.nodes_dict[node] = Q_Node(self,node,self.rank,self.average_info,self.Rs_Labels,self.Ms,self.Ns,self.memo_archive)
    
    def serve_demand(self,queue_nodes,order): # This function expects Decision to be a dict such as {AB : 2}
        controlling_node = queue_nodes[int(self.rng.random() <= .5)] # Randomly select a controlling node for this transition
        self.getNode(controlling_node).consume_pairs(queue_nodes,order)
    
    def apply_swap(self,tr_label,n): 
        node = self.nodes_dict[tr_label[2]]
        recv_queue = (tr_label[0],tr_label[-1])
        recv_node = next(iter(recv_queue)) # Node to which we'll communicate the success operation. Of course we should do it to both partners, but one is enough for this level of abstraction. 
        successes = node.attempt_transition(tr_label,n)
        self.getNode(recv_node).enqueue_success(recv_queue,successes)

    def getNode(self,node):
        return self.nodes_dict[node]
    
    def node_schedule(self,node):
        self.getNode(node).schedule()
    
    def node_scramble_and_lint(self,node):
        self.getNode(node).scramble_and_lint()
    
    def node_calculate_constr_weights(self,node,info):
        self.getNode(node).calculate_constr_weights(info)
        
    def snapshot(self):
        self.Backlog_t = {frozenset(l):(self.getLink(l).getEbitBacklog(),self.getLink(l).getDemandBacklog()) for l in self.links_dict}
        return self.Backlog_t
    
    def getAvailableInformation(self):
        info = dict()
        info["Averages"] = self.average_info
        info["Backlog_t"] = self.snapshot()
        if ui.policy["information access"] == "Full":
            info["Backlog_t1"] = self.snapshot() # Notice that this snapshot is taken at t+1, not t: that's what differentiates this call from the one· from the simulation kernel.
        return info
        
    def schedule(self):
        info = self.getAvailableInformation()
        if ui.policy["localization"] == "Node-Local":
            for node in self.nodes_dict: 
                self.node_calculate_constr_weights(node,info) # Send the calc_constraints signal to the nodes in series.
                self.node_schedule(node) # Send the solve_lp signal to the nodes in series.
                self.node_scramble_and_lint(node)
        elif ui.policy["localization"] == "Global":
            self.scheduler.calculate_constr_weights(**info)
            Rs = self.scheduler.schedule()
            self.scheduled_decision = dict(zip(self.Rs_Labels,Rs))
            self.relay_global_decision()
            for node in self.nodes_dict: 
                self.node_scramble_and_lint(node)
    
    def relay_global_decision(self):
        for nd in self.nodes_dict:
            self.getNode(nd).set_global_decision(self.scheduled_decision)
            
    def apply_decision(self): 
        self.rng.shuffle(self.node_order)
        for rk in range(self.MaxRank+1):
            for node in self.node_order:
                self.getNode(node).apply_decision(rk)
    
    
    def relay_success(self,recv_queue,successes):
        recv_node = recv_queue[0]
        self.getNode(recv_node).enqueue_success(recv_queue,successes)