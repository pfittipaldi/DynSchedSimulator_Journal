from Sim_Kernel import Sim
import numpy as np
from time import time
import matplotlib.pyplot as plt
import multiprocessing as mp
from datetime import datetime
import User_Input as ui

if ui.PhotonLifeTime == "Inf":
    LossParam = 1
else:
    LossParam = np.exp(-ui.t_step/ui.PhotonLifeTime)

DemRates1 = np.linspace(ui.minload,ui.maxload,ui.n_points)
DemRates2 = np.linspace(ui.minload,ui.maxload,ui.n_points)

print("###############Recap:###############")
print(f"- {ui.topologyname} topology, {ui.n_points}x{ui.n_points} pixels")
print(f"- Losses (1-eta): {1 - LossParam}")
print(f"- Service pairs: - {ui.SPairs[0]}, {DemRates1[0]} - {DemRates1[-1]} Hz,")
print(f"                 - {ui.SPairs[1]}, {DemRates2[0]} - {DemRates2[-1]} Hz,")
print(f"-                - {ui.SPairs[2:]} static random pairs, {ui.DemRateRest} fixed, non-plotted")
print(f"Parallel Run: {ui.ParallelRun}")
print(f"Scheduler: {ui.policy['name']}")

if __name__ == '__main__':
    
    now = datetime.now().strftime("%H:%M:%S")
    print(f"Starting simulation at {now}")
    
    AvD_RAW = [] 

    nprocs = int(mp.cpu_count()/2) # Number of workers in the pool. /2 to have as many workers as there are physical cores.
                                   # If your CPU is not multithreaded, remove the /2.

    InputList = []
    t1 = time()
    
    
    
    SPair_1 = ui.SPairs[0]
    SPair_2 = ui.SPairs[1] # Storing these two away before the frozenset cast, to 
                        # be able to address them by index in the plotting section
    
    for i,_ in enumerate(ui.SPairs): # Building a list of dictionaries, each with the form 
                                  # {pair1 : demrate1, pair2 : demrate2...}. as the simulation kernel expects. 
        ui.SPairs[i] = frozenset(ui.SPairs[i])
    for r1 in DemRates1:
            for r2 in DemRates2:
                rateslist = [r1,r2] + (len(ui.SPairs)-2)*[ui.DemRateRest]
                SimInput = dict(zip(ui.SPairs, rateslist))
                InputList.append(SimInput)
    
    # The memo object is a dictionary that is SHARED by all the pixels. See docs
    # for details. 
    if ui.ParallelRun:
        with mp.Manager() as manager:
            memo_pixels = manager.dict() # Pareto boundary memoization
            memoList_pix = [memo_pixels for i in InputList]
            with manager.Pool(processes=nprocs) as p:
                output_RAW = p.starmap(Sim,zip(InputList,memoList_pix))
                p.close()
                p.join()
    else: 
        from functools import partial   
        memo_pixels = dict()
        memo_internal = dict()
        MemoizedSim = partial(Sim,memo_pix = memo_pixels)
        output_RAW = list(map(MemoizedSim,InputList))
    
    t2 = time()-t1
    now = datetime.now().strftime("%H:%M:%S")
    print(f"Ending at {now}. Elapsed time: {np.floor(t2/60)} minutes and {(t2/60-np.floor(t2/60))*60:.2f} seconds")
    
    # Output conditioning and plotting 
    
    AvD_RAW, Dt_RAW = zip(*output_RAW)
    
    
    # print("Starting cache assembly...")
    # archive = dict()
    # for arc in archive_RAW:
    #     archive.update(arc)
    # print("Cache generated. Writing to disk...")
    # np.save("controller_cache",archive)
    
    lenD = len(Dt_RAW[0])
    
    Dt = np.array(Dt_RAW).reshape((ui.n_points,ui.n_points,lenD),order="F")
    Dt = np.flipud(Dt)
    
    AvD = np.array(AvD_RAW).reshape((ui.n_points,ui.n_points),order="F")
    AvD = np.flipud(AvD)

    plt.figure()
    
    if ui.LogScale == True:
    	import matplotlib.colors as mplc
    	plt.imshow(AvD,norm=mplc.SymLogNorm(1e-1,vmax=ui.PlotCutoff))
    else:
    	plt.imshow(AvD,vmax = ui.PlotCutoff)
    plt.colorbar()
    
   
    xlabels = ['{:.2f}'.format(i) for i in np.linspace(DemRates1[0],DemRates1[-1],ui.n_labels)/1000]
    ylabels = ['{:.2f}'.format(i) for i in np.linspace(DemRates2[0],DemRates2[-1],ui.n_labels)/1000]
    ylabels = np.flip(ylabels)

        
    plt.xticks(np.linspace(0,ui.n_points-1,ui.n_labels),xlabels,rotation=70)
    plt.yticks(np.linspace(0,ui.n_points-1,ui.n_labels),ylabels)
    plt.xlabel(f"Average demand rate across pair {SPair_1[0]}-{SPair_1[1]}, kHz")  
    plt.ylabel(f"Average demand rate across pair {SPair_2[0]}-{SPair_2[1]}, kHz")
    
    short_name = ui.policy["short_name"]
    
    plt.title(f"Average Demand Backlog,{short_name},{ui.topologyname}")
    plt.savefig(f"{ui.n_points}x{ui.n_points}_{short_name}_{ui.topologyname}_{now}_{nprocs}t_{ui.comment}.pdf",bbox_inches="tight")
    
    inputs = dict(ipt for ipt in ui.__dict__.items() if ipt[0][0] != "_") # Storing all the user input variables in this list for saving
    
    np.savez(f"{ui.n_points}x{ui.n_points}_{short_name}_{ui.topologyname}_{now}_{nprocs}t_{ui.comment}", **inputs ,AvD=AvD, Dt=Dt)

    if ui.plot_temporal_plots:
        fig, ax = plt.subplots(ui.n_points, ui.n_points, sharey=True)
        for i in range(ui.n_points):
            for j in range(ui.n_points):
                if AvD[i,j] != np.inf:
                    ax[i,j].plot(Dt[i,j,:])
	    
        fig2, ax2 = plt.subplots(ui.n_points, ui.n_points)
        for i in range(ui.n_points):
            for j in range(ui.n_points):
                if AvD[i,j] != np.inf:
                    ax2[i,j].plot(Dt[i,j,:])
        plt.savefig(f"{ui.n_points}x{ui.n_points}_{short_name}_{ui.topologyname}_{now}_{nprocs}t_{ui.comment}_temporal.pdf",bbox_inches="tight")

    
    
