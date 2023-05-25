#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 17 11:59:26 2023

@author: paolo
"""
from SchedulingModule import SchedulingModule
import User_Input as ui
import numpy as np
from itertools import chain

class Q_Node: # Single node in the quantum network. 
    def __init__(self,controller,name,rank,averages,Rs_labels,Ms,Ns,memo_archive):
            self.name = name
            self.connectedLinks = {} # {nodes : Queueobject}, for ease of access
            self.hasscheduler = False
            self.controller = controller
            self.Ms = Ms
            self.Ns = Ns
            self.Rs_labels = Rs_labels
            self.rank = rank
            self.averages = averages
            if ui.policy["localization"] == "Node-Local":
                self.boot_scheduler(memo_archive)
            self.rng = np.random.default_rng()
                
    def connect_queue(self,queue): # Called by the QController when bootstrapping the network.
        self.connectedLinks[queue.nodes] = queue 
    
    def consume_pairs(self,queue,order): 
        self.getLink(queue).ServeDemand(order)
        
    def getLink(self,link):
        link = frozenset(link)
        return self.connectedLinks[link]
        
    def attempt_transition(self,transition,n):
        queue1 = self.getLink((transition[0],transition[2]))
        queue2 = self.getLink((transition[2],transition[4]))
        successes = min(queue1.Measure(n),queue2.Measure(n),n) # Either we managed to serve all demands, or there was not enough resource. 
        return successes
    
    def enqueue_success(self,recv_queue,n):
        self.getLink(recv_queue).ReceiveSwaps(n)
    
    def boot_scheduler(self,memo_archive):
        if not self.hasscheduler:
            self.hasscheduler = True
            self.scheduler = SchedulingModule(self.Ms, self.Ns,memo_archive)
    
    def snapshot(self):
        self.local_Backlog_t1 = {l:(self.getLink(l).getEbitBacklog(),self.getLink(l).getDemandBacklog()) for l in self.connectedLinks}
        
    def calculate_constr_weights(self,info):
        if ui.policy["information access"] == "Node-Local":
            info["Local_Backlog_t1"] = self.snapshot()
        self.scheduler.calculate_constr_weights(**info)
        
    def schedule(self):
        Rs = self.scheduler.schedule()
        self.scheduled_decision = dict(zip(self.Rs_labels,Rs))
    
    def set_global_decision(self,decision):
        self.scheduled_decision = decision
    
    def scramble_and_lint(self): #Given a dictionary with a scheduling decision, return it sorted by rank and scrambled.
        decision = {dec : self.scheduled_decision[dec] for dec in self.scheduled_decision if self.scheduled_decision[dec] != 0}
        to_lint = list(decision.keys())
        for dec in to_lint:
            if len(dec) == 2 and self.name not in dec: # If this is a consumption order for a disconnected queue, purge it
                decision.pop(dec)
            elif len(dec) == 5 and dec[2] != self.name:
                decision.pop(dec)
        self.scheduled_decision = dict()
        clean_decision = decision
        if clean_decision != {}:
            rank = self.rank
            for i in rank:
                self.rng.shuffle(rank[i])
            scrambled_order = list(chain(*rank.values()))
            scrambled_decision = {dec:decision[dec] for dec in scrambled_order if dec in clean_decision}
            self.scheduled_decision = scrambled_decision

    def apply_decision(self,rk): 
      decision = self.scheduled_decision
      if decision != {}:
          for order in decision:
              if order in self.rank[rk]:
                  if len(order) == 2:
                      self.consume_pairs(order,decision[order])
                      self.scheduled_decision[order] = 0 # Clear the decision once it has been applied. 
                  elif len(order) == 5:
                      self.apply_swap(order,decision[order])
                      self.scheduled_decision[order] = 0
      
      
    def apply_swap(self,tr_label,n): 
        recv_queue = (tr_label[0],tr_label[-1])
        successes = self.attempt_transition(tr_label,n)
        self.controller.relay_success(recv_queue,successes)
    
  