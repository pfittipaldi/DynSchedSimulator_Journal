#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simulator parameters: These inputs are specific to the simulator. 
"""
#########################################
#           SIMULATION INPUTS           #
#########################################

PhotonLifeTime = "Inf" #10e-6 # average photon lifetime inside the quantum memories, s 
                       # Should be always higher than time step.
                       # Set to "Inf" for lossless simulation.

traffic_model = "I"
batch_demand_period = 0.5  
MemorySlots = 100   
                
t_step = 0.01 #1e-6; # Length of the time step, s

time_steps = int(2e3); # Number of steps to simulate per pixel

memo_len=int(time_steps) # How many configurations should be memoized

n_points = 5 # The final stability plot will have a resolution of n_points*n_points

minload = 100 # Minimum load across the two plotted service pairs, Hz
            # If possible, avoid setting this to zero, prefer a low non-zero value.

maxload = 10000 # Maximum load across the two plotted service pairs, Hz

plot_temporal_plots = True # If true, the backlog of the plotted pairs is plotted in time for each pixel. Use this with a 
                            # low (<=6) value of n_points to have more readable figures. 

#########################################
#          OUTPUT CONDITIONING          #
#########################################

PlotCutoff = 1000 # Where the yellow region starts on the plot. Put this reasonably lower than HIGH_THRESHOLD to allow for random fluctuation to fully play out. 

#Thresholds for paretoboundary optimization: If a point has average queue length 
# higher than HIGH_THRESHOLD, all points with higher load are skipped without 
# calculation. The opposite works for LOW_THRESHOLD.  
HIGH_THRESHOLD = 1500
LOW_THRESHOLD = 0

LogScale = False # Whether to plot in log (linearized close to 0) or lin scale.

n_labels = 9 # Number of ticks on the stability plot axes

#########################################
#              MISC INPUTS              #
#########################################

comment = "QuispVal" #Misc comment that will be appended on the results files' names.

ParallelRun = False    # Huge performance gain if True. This should be set to 
                      # False only when debugging
