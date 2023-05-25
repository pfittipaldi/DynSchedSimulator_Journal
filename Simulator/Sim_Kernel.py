#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 10 09:30:44 2021

@author: paolo
"""

### INPUT
from LinkPhysicsEngine import LinkPhysicsEngine
import numpy as np
from Link import Link
from Q_Controller import Q_Controller
import MGeneration as mg
from itertools import chain
import networkx as nx
import User_Input as ui


def Sim(BatchInput,memo_pix):   
    flatInput = tuple(zip(*BatchInput.items())) # Flattening the input for memoization
    
    for i in memo_pix.keys():
        flatMemo = i
        # IF I have in memory a point that was UNSTABLE and at a LOWER load than current input:
        if flatInput[1][0] >= flatMemo[1][0] and flatInput[1][1] >= flatMemo[1][1] and memo_pix[i][0] >= ui.HIGH_THRESHOLD:
            output = memo_pix[i]
            return output
        # IF I have in memory a point that was STABLE and at a HIGHER load than current input:
        elif flatInput[1][0] <= flatMemo[1][0] and flatInput[1][1] <= flatMemo[1][1] and memo_pix[i][0] <= ui.LOW_THRESHOLD:
            output = memo_pix[i]
            return output
    
    if ui.PhotonLifeTime == "Inf":
        LossParam = 1
    else:
        LossParam = np.round(np.exp(-ui.t_step/ui.PhotonLifeTime),2)
    
    # Building the M matrix 
    qnet = mg.eswapnet()
    for rt in ui.routes:
        qnet.addpath(rt)
    M, Links_labels, Transitions_labels = qnet.QC.matrix()
    
    Rs_Labels = Transitions_labels + Links_labels # List of the labels of Ms's columns.
    
    nI_matrix = -np.identity(len(Links_labels)) #Matrix for the demand part
    Ms = np.concatenate((M,nI_matrix),1) # Full "Big M" matrix
    Ns = np.concatenate((np.zeros((len(M),len(M[0]))),nI_matrix),1) # Auxiliary matrix analogous to big M but for demands
    
    
    
    # Ranking all the queues and transitions to derive the execution order, with extra care for cycles.
    # See docs for in-depth explanation of this section. 
    rank = {}
    currentrank = 0
    QG=qnet.QC.graph()
    cycles = list(nx.simple_cycles(QG)) # Listing all the cycles in the routing graph, because they need special care in the ranking process
    watchlist = list(chain(*cycles))
    watchlist.sort(key=lambda x : len(x))
    while(len(QG) > 0):
        rank[currentrank] = []
        bottom_layer = [v for v in QG if QG.in_degree(v) == 0]
        if bottom_layer == []:
            bottom_layer = [i for i in watchlist if QG.in_degree(i) == 1 and len(i) != len(rank[currentrank-1][0])]
        rank[currentrank] += bottom_layer
        currentrank+=1
        QG.remove_nodes_from(bottom_layer)
    
    # Building the links 
    Links_list = [Link(tq[0],tq[1],LossParam) for tq in Links_labels]
    fset_labels = [frozenset(lk) for lk in Links_labels]
    Links_dict = dict(zip(fset_labels,Links_list))
    [q.SetPhysical(ui.ArrRates[q.nodes],ui.t_step) for q in Links_list if q.nodes in ui.ArrRates]
    [q.SetService(BatchInput[q.nodes],ui.t_step) for q in Links_list if q.nodes in BatchInput]
    
     
    #Instantiating the Quantum Controller and the Physics Engine
    q_controller = Q_Controller(qnet.G,Links_dict,rank,Rs_Labels,Ms,Ns) 
    p_engine = LinkPhysicsEngine(Links_list)
    
    # Defining the building blocks of the optimization problem.
    # From now on, every variable with an s in front is to be read as \tilde{x}
    
    
    to_exclude = int(ui.time_steps/10)
    AccDt = []
    
    for Maintimestep in range(ui.time_steps):
        Dt = [l.getDemandBacklog() for l in Links_list]
        AccDt.append(sum(Dt))
        q_controller.snapshot() # The q_controller takes a snapshot of Q(t) and D(t): this information is assumed available in all our policies.
        p_engine.step()
        q_controller.schedule()    
        q_controller.apply_decision()
    
    DQueueAv = sum(AccDt[to_exclude:])/((ui.time_steps-to_exclude)*len(BatchInput))
    
    # FinalArchive = q_controller.getArchive()
    
    if DQueueAv >= ui.HIGH_THRESHOLD:
        to_store = tuple(zip(*BatchInput.items()))
        memo_pix[to_store] = (np.inf,[np.inf]*ui.time_steps)
    elif DQueueAv <= ui.LOW_THRESHOLD:
        to_store = tuple(zip(*BatchInput.items()))
        memo_pix[to_store] = (0,[0]*ui.time_steps)
    
    return DQueueAv, AccDt #, FinalArchive