#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simulator parameters: These inputs are specific to the simulator. 
"""
#########################################
#           SIMULATION INPUTS           #
#########################################

PhotonLifeTime = 10e-6 # average photon lifetime inside the quantum memories, s 
                       # Should be always higher than time step.
                       # Set to "Inf" for lossless simulation.
                       
t_step = 1e-6; # Length of the time step, s

time_steps = int(1e3); # Number of steps to simulate per pixel

memo_len=int(time_steps) # How many configurations should be memoized

n_points = 17 # The final stability plot will have a resolution of n_points*n_points

minload = 1 # Minimum load across the two plotted service pairs, Hz
            # If possible, avoid setting this to zero, prefer a low non-zero value.

maxload = 1000000 # Maximum load across the two plotted service pairs, Hz

plot_temporal_plots = False # If true, the backlog of the plotted pairs is plotted in time for each pixel. Use this with a 
                            # low (<=6) value of n_points to have more readable figures. 

#########################################
#          OUTPUT CONDITIONING          #
#########################################

PlotCutoff = 100 # Where the yellow region starts on the plot. Put this reasonably lower than HIGH_THRESHOLD to allow for random fluctuation to fully play out. 

#Thresholds for paretoboundary optimization: If a point has average queue length 
# higher than HIGH_THRESHOLD, all points with higher load are skipped without 
# calculation. The opposite works for LOW_THRESHOLD.  
HIGH_THRESHOLD = 35
LOW_THRESHOLD = 0

LogScale = True # Whether to plot in log (linearized close to 0) or lin scale.

n_labels = 9 # Number of ticks on the stability plot axes

#########################################
#              MISC INPUTS              #
#########################################

comment = "Final" #Misc comment that will be appended on the results files' names.

ParallelRun = True    # Huge performance gain if True. This should be set to 
                      # False only when debugging

ArrRates = {
frozenset(('A','E')) : 1000000,
frozenset(('A','B')) : 1000000,
frozenset(('B','F')) : 1000000,
frozenset(('C','H')) : 1000000,
frozenset(('C','D')) : 1000000,
frozenset(('D','I')) : 1000000,
frozenset(('E','K')) : 1000000,
frozenset(('E','F')) : 1000000,
frozenset(('F','G')) : 1000000,
frozenset(('G','L')) : 1000000,
frozenset(('G','H')) : 1000000,
frozenset(('H','M')) : 1000000,
frozenset(('H','I')) : 1000000,
frozenset(('I','N')) : 1000000,
frozenset(('I','J')) : 1000000,
frozenset(('J','O')) : 1000000,
frozenset(('K','P')) : 1000000,
frozenset(('L','R')) : 1000000,
frozenset(('L','M')) : 1000000,
frozenset(('M','S')) : 1000000,
frozenset(('M','N')) : 1000000,
frozenset(('N','O')) : 1000000,
frozenset(('O','T')) : 1000000,
frozenset(('P','U')) : 1000000,
frozenset(('P','Q')) : 1000000,
frozenset(('Q','V')) : 1000000,
frozenset(('Q','R')) : 1000000,
frozenset(('R','W')) : 1000000,
frozenset(('R','S')) : 1000000,
frozenset(('T','X')) : 1000000,
frozenset(('U','Y')) : 1000000,
frozenset(('U','V')) : 1000000,
frozenset(('V','Z')) : 1000000,
frozenset(('V','W')) : 1000000,
frozenset(('W','a')) : 1000000,
frozenset(('X','d')) : 1000000,
frozenset(('Y','Z')) : 1000000,
frozenset(('Z','a')) : 1000000,
frozenset(('a','b')) : 1000000,
frozenset(('b','c')) : 1000000,
frozenset(('c','d')) : 1000000,
}
topologyname = "pG(36,4,0.3), 10p"
routes = ['JIHGFEKPUY', 'JINMLRQVZY', 'dcbaZYUPKEA', 'dXTONMLGFEA', 'ONMS', 'OJIHGLRS', 'Xdcba', 'XTONMLRWa', 'ONMLRW', 'OJIHGLRW', 'MNOTXd', 'MLRWabcd', 'Zab', 'ZVQRLMNOTXdcb', 'VWab', 'VQRLMNOTXdcb', 'DIN', 'DCHMN', 'GLRWa', 'GLRQVZa']
SPairs = [('J', 'Y'), ('d', 'A'), ('O', 'S'), ('X', 'a'), ('O', 'W'), ('M', 'd'), ('Z', 'b'), ('V', 'b'), ('D', 'N'), ('G', 'a')]
DemRateRest = 300000
policy = {'name': 'Full Information MaxWeight', 'short_name': 'FIMW', 'localization': 'Global', 'information access': 'Full', 'type': 'Linear'}