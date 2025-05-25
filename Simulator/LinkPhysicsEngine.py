#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 10 11:13:27 2021

@author: paolo

This class contains functions that interface to all queues in the system.
"""
import numpy as np
class LinkPhysicsEngine: 
    def __init__(self,Links):
        self.Links = Links
    
    def generate(self):
        A = np.zeros(len(self.Links))
        for i in range(len(self.Links)):
            A[i] = self.Links[i].Generate();
        return A
    
    def losses(self,):
        L = np.zeros(len(self.Links))
        for i in range(len(self.Links)):
            L[i] = self.Links[i].Loss();
        return L
    
    def receive_demand(self,simtime):
        B = np.zeros(len(self.Links))
        for i in range(len(self.Links)):
            B[i] = self.Links[i].Demand(simtime);
        return B
    
    def step(self,simtime):
        A = self.generate()
        L = self.losses()
        B = self.receive_demand(simtime)
        return A, L, B
        