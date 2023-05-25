#! /usr/bin/python

# This module contains the code we used to generate the M matrix. See smalltest() at the
# bottom for a usage example. 

import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

inf=float("inf")

class transition():
    def __init__(self, inputs, outputs, name=''):
        self.inputs  = inputs
        self.outputs = outputs
        self.name = name
    def __str__(self):
        return "transition '" + self.name +"' {" + ", ".join(x for x in self.inputs) \
                + "} -> {" \
                + ", ".join(y for y in self.outputs) + "}"  
                
class queueconstraints():
    # This class encodes the set of transitions associated with the quantum network. 
    def __init__(self):
        self.queues=[]
        self.transitions=set()
        self.transitionsfrom=dict()
        self.transitionsto=dict()
        self.transitionsreference = set() # I introduced this to keep track of which transitions are already in QC.
                                          # ...with an object that is a builtin type.
    
    def addqueue(self, label):
        "if queue already exists, do nothing"
        if label not in self.queues: 
            self.queues.append(label)
            self.transitionsfrom[label]=[]
            self.transitionsto[label]=[]

    
    def addtransition(self, transition):
        if str(transition) not in self.transitionsreference:
            def qaction(q, dic):
               self.addqueue(q)
               dic[q]=transition
            for q in transition.inputs : qaction(q, self.transitionsfrom)
            for q in transition.outputs: qaction(q, self.transitionsto)
            self.transitions.add(transition)
            self.transitionsreference.add(str(transition)) # Added this line to avoid having duplicates 
                                                           # while circumventing the fact that the "in" operator 
                                                           # is not defined for custom classes.

    def graph(self):
        G = nx.DiGraph()
        for t in self.transitions:
            G.add_edges_from(((inp, t.name) for inp in t.inputs))
            G.add_edges_from(((t.name, out) for out in t.outputs))
        return G
    
    def matrix(self): # Generate the M matrix associated with the provided routing
        list_queues = self.queues
        q_i = {q:i for i,q in enumerate(list_queues)}
        list_transitions=list(self.transitions)
        transition_names =[t.name for t in list_transitions]
        M = np.zeros((len(list_queues), len(list_transitions)))
        for j,t in enumerate(list_transitions):
              for q in t.inputs : M[q_i[q],j] -=1
              for q in t.outputs: M[q_i[q],j] +=1
        return M, list_queues, transition_names

def edgelabel(u, v, sep=''):
     return sep.join(str(x) for x in (u,v))

class eswapnet():
    def __init__(self):
        self.QC=queueconstraints()
        self.G =nx.Graph()
        
    def addvertex(self,label):
        self.G.add_node(label)
        
    def addvertices(self,itr):
        self.G.add_nodes_from(itr)
        
    def addedge(self, x, y):
        x, y = sorted((x,y))
        label=edgelabel(x,y)
        self.G.add_edge(x, y, label=label)
        self.QC.addqueue(label)
                
    def addpath(self, path): #path is acyclic
        lp = len(path)
        
        self.addedge(*path[-2:])
        for i in range(lp-2):
            self.addedge(*path[i:i+2])
            for j in range(i+1,lp-1):
                for k in range(j+1,lp):
                    a,c = sorted((path[i],path[k]))
                    b = path[j]
                    self.QC.addtransition(
                        transition([edgelabel(*sorted(tpl)) for tpl in ((a,b),(b,c))],
                                    [edgelabel(a,c)], 
                                    name=f'{a}[{b}]{c}' ) )
def smalltest():
    qnet = eswapnet()
    qnet.addpath('abcd')
    qnet.addpath('bcde')
    qnet.addpath('bgd')
    M, qs, ts = qnet.QC.matrix()
    plt.figure()
    nx.draw(qnet.G, with_labels=True)
    
    QG=qnet.QC.graph()
    QG.graph['graph']={'rankdir': 'TB'}
    plt.figure()
    #pos = nx.nx_pydot.pydot_layout(QG, prog='dot')
    pos = nx.nx_agraph.pygraphviz_layout(QG, prog='dot')
    nx.draw(QG, pos, with_labels=True, node_shape='s') #one of 'so^>v<dph8'
    return qnet

