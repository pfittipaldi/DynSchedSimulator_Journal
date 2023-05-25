#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 15 15:59:43 2023

@author: paolo
"""

import numpy as np
import gurobipy as gp
from gurobipy import GRB
import User_Input as ui
from contextlib import redirect_stdout
from os import devnull
from scipy.sparse import dok_matrix

class SchedulingModule:
    def __init__(self,Ms,Ns,memo_archive):
        self.p_name = ui.policy["name"]
        self.rng = np.random.default_rng()
        self.Ms = Ms
        self.Ns = Ns
        self.G = np.vstack((self.Ms,self.Ns)) #Constraints matrix
        self.P = self.Ns.T@self.Ns # Quadratic penalty for the quad schedulers
        with redirect_stdout(open(devnull,"w")): # This is just to suppress gurobi's output, couldn't manage otherwise
            self.env = gp.Env()
        self.memo = memo_archive # In-scheduler memoization
        
    def greedy_schedule(self):
        sol = [np.inf]*(len(self.Ms[0]))
        return sol
    
    def maxweight_schedule(self):
        with gp.Model(env=self.env) as prob:
            prob.Params.OutputFlag = 0
            prob.Params.threads = 1
            R = prob.addMVar(len(self.w),vtype=GRB.INTEGER)
            expr = self.w@R
            prob.setObjective(expr,GRB.MINIMIZE)
            constrleq = -self.G@R <= self.forcing_term
            prob.addConstr(constrleq)
            prob.optimize()
            sol = np.array([v.x for v in prob.getVars()],dtype=np.uintc)
            return sol
    
    def quad_schedule(self):
        with gp.Model(env=self.env) as prob:
            prob.Params.OutputFlag = 0
            prob.Params.threads = 1
            R = prob.addMVar(len(self.w),vtype=GRB.INTEGER)
            aux = R@self.P
            expr = 0.5*aux@R + self.w@R
            prob.setObjective(expr,GRB.MINIMIZE)
            constrleq = -self.G@R <= self.forcing_term
            prob.addConstr(constrleq)
            prob.optimize()
            sol = np.array([v.x for v in prob.getVars()],dtype=np.uintc)
            return sol
    
    def custom_schedule(self): # Implement your custom scheduler here. 
        print("Edit the custom_schedule method inside SchedulingModule.py to test your own schedulers")
        exit()
    
    def calculate_constr_weights(self,Backlog_t=None,Averages=None,Backlog_t1=None,Local_Backlog_t1=None):
        alpha = Averages["alpha"]
        beta = Averages["beta"]
        eta = Averages["eta"]
        
        if Backlog_t1 is not None:
            Qt1, Dt1 = zip(*Backlog_t1.values())
            self.forcing_term = np.hstack((Qt1,Dt1)) 
            self.w = Dt1@self.Ns 
        else:
            Qt, Dt = zip(*Backlog_t.values())
            Exp_Qt1 = np.multiply(eta,Qt) + alpha
            Exp_Dt1 = np.array(Dt) + np.array(beta)
            
            if Local_Backlog_t1 is not None: # Correct local constraints, if available
                zippedBacklogs = zip(Exp_Qt1,Exp_Dt1)
                Exp_Backlog_t1 = dict(zip(Backlog_t.keys(),zippedBacklogs)) # {link : (Qt,Dt)}
                for l in Local_Backlog_t1:
                    Exp_Backlog_t1[l] = Local_Backlog_t1[l]
                Exp_Qt1,Exp_Dt1 = zip(*Exp_Backlog_t1.values())
                
            self.forcing_term = np.hstack((Exp_Qt1,Exp_Dt1))
            self.w = Exp_Dt1@self.Ns
    
    def schedule(self):
        if ui.policy["type"] == "Custom":
            Rs = self.custom_schedule()
        elif ui.policy["type"] == "Greedy":
            Rs = self.greedy_schedule()
        else: 
            dense_state_key = np.hstack((self.w,self.forcing_term))
            sparse_state_key = dok_matrix(np.atleast_2d(dense_state_key))
            curr_state_key = frozenset(sparse_state_key.items())
            
            if curr_state_key not in self.memo:
                Rs = self.maxweight_schedule() if ui.policy["type"] == "Linear" else self.quad_schedule() if ui.policy["type"] == "Quadratic" else None
                self.memo[curr_state_key] = Rs
            else:
                #print("skipped one!")
                Rs = self.memo[curr_state_key]
                
        if Rs is None:
            print("Unrecognized scheduling policy. Accepted types:")
            print("Custom, Greedy, Optimized")
            print("Accepted degrees:")
            print("Linear, Quadratic")
            exit()
        return Rs