#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This class models one link in the network, i.e. one edge in the extended set. It is controlled
by Nodes and by the Physics Engine.

"""
import numpy as np

class Link:
    def __init__(self,nd1,nd2,LossParam):
        self.nodes = frozenset([nd1,nd2]) # End nodes of the edge
        self.type = "virtual" # virtual or physical queue
        self.serv = "regular" # regular or service pair, i.e. whether it receives demand
        self.Ebits = 0; # Ebits in the ebit queue
        self.demands = 0; # Demands in the demand queue
        self.LossParam = LossParam
        self.rng = np.random.default_rng()
        self.traffic_model = "P" # "P" = Poissonian, "I" = Impulse (Batch of X demands every Y seconds)
        self.Poiss_Demands = 0
        self.Poiss_Ebits = 0
        self.batch_demand_amount = 0
        self.batch_demand_period = 0
        
    def SetPhysical(self,arr_rate_s,t_step):
        self.type = "physical"
        alpha = arr_rate_s*t_step
        self.Poiss_Ebits = alpha # Parameter for the Poisson Distribution of photon arrivals

    def SetVirtual(self):
        self.type = "virtual"
        self.Poiss_Ebits = 0

    def SetService_P(self,poiss_rate_tstep,tstep):
        self.traffic_model = "P"
        self.serv = "service" # If the queue is service, it receives demands.
        DemArrRate_steps = poiss_rate_tstep*tstep # casting the rate per second to a rate per time step
        self.Poiss_Demands = DemArrRate_steps # Parameter for the Poisson Distribution
        return self
    
    def SetService_I(self,batch_amount,batch_period):
        self.traffic_model = "I"
        self.serv = "service" # If the queue is service, it receives demands.
        self.batch_demand_amount = batch_amount
        self.batch_demand_period = batch_period
        return self
    
    def getEbitBacklog(self):
        return self.Ebits
    
    def getDemandBacklog(self):
        return self.demands

    def Measure(self,n):
        oldbacklog = self.Ebits
        self.Ebits = max(self.Ebits-n,0)
        return oldbacklog - self.Ebits
    
    def ReceiveSwaps(self,n):
        self.Ebits+=n

    def ServeDemand(self,n):
        attempts = min(n,self.demands)
        successes = self.Measure(attempts)
        self.demands -= successes
        if self.demands < 0:
            self.demands = 0
        return successes

    def Generate(self):
        rng = self.rng
        if (self.type == "physical"):
            generated = rng.poisson(self.Poiss_Ebits)
            self.Ebits += generated
            return generated
        else:
            return 0

    def Loss(self):
        rng=self.rng
        to_check = self.Ebits
        lost = sum(rng.random(int(to_check)) <= (1-self.LossParam))
        self.Ebits -= lost
        return lost
    
    def Demand(self,simtime):
        if self.traffic_model == "P":
            return self.Demand_P()
        elif self.traffic_model == "I":
            return self.Demand_I(simtime)
        else:
            print("Unrecognized traffic model: " + self.traffic_model + ". Valid models are P or I")
    
    def Demand_P(self): 
            D = 0;
            if self.serv == "service": 
                D = self.rng.poisson(self.Poiss_Demands)
                self.demands += D
            return D
    
    def Demand_I(self,simtime):
        if self.serv == "service": 
            if (np.isclose(np.fmod(simtime,self.batch_demand_period), 0)):
                self.demands += self.batch_demand_amount
                return self.batch_demand_amount
            else:
                return 0
                
    
    def getAverages(self):
        return (self.Poiss_Ebits,self.Poiss_Demands,self.LossParam)
    
