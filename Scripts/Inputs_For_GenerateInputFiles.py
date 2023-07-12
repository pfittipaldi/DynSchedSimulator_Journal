"""
Inputs to the GenerateInputFiles.py script: these specify the topology for the simulation, the routing parameters, the policies to simulate....
"""

#########################################
#       INPUT FILE(S) GENERATION        #
#########################################
Graph_Type = "ER" # WS - WATTS-STROGATZ, 
                 # ER - ERDOS-RENYI, 
                 # G - GRID, pG - GRID, THEN REMOVE EACH EDGE WITH PROB. p 
                 # C - CUSTOM, user-provided

G = None # If you set Graph_Type to "C", provide a NetworkX Graph here. Otherwise, leave this as None. 

n_nodes = 25 # Number of nodes in the topology, <= 52

n_neighbors = 4 # If Graph_Type is WS, this is the number of neighbors each node is connected to.

p = .12 # p parameter in the random graph generation models.

IncludePhysicalQueues=False # Whether Physical links can be drawn as random service pairs in the simulation. 


GenRate = 1000000 # Generation rate across the physical links, Hz

Num_Pairs = 10 # Number of service pairs (Parasitic pairs = Num_Pairs - 2)

Num_Routes = 2 # Routes per service pair

path_pop_prob = .2 # When requesting more than one path, the n-th path will be 
                   # calculated by removing each edge of the previous shortest 
                   # path with probability p. 

Configs_toGen = 10 # Sets of parasitic pairs to generate

Max_Ppairs_Load = 300000 # maximum load over the parasitic pairs, Hz

N_Load_Points = 4 # Number of load points for the parasitic pairs

SPair1=None #If you don't define them here, the code will show you the topology and prompt you to choose
SPair2=None #The code expects them to be defined as a string, like "AB" or "aB"
AutoSelectPairs = True


policies_to_simulate = [
    
    {
    "name" : "Greedy",
    "short_name" : "G",
    "localization" : "Node-Local",
    "information access" : "Node-Local",
    "type" : "Greedy"
    },
    
    {
    "name" : "Full Information MaxWeight",
    "short_name" : "FIMW",
    "localization" : "Global",
    "information access" : "Full",
    "type" : "Linear"
    },
    
    {
    "name" : "Average Information MaxWeight",
    "short_name" : "AIMW",
    "localization" : "Global",
    "information access" : "All Average",
    "type" : "Linear"
    },
    
    {
    "name" : "Local Information MaxWeight",
    "short_name" : "LIMW",
    "localization" : "Node-Local",
    "information access" : "Node-Local",
    "type" : "Linear"
    }
    
    # {
    # "name" : "Full Information Quadratic",
    # "short_name" : "FIQ",
    # "localization" : "Global",
    # "information access" : "Full",
    # "type" : "Quadratic"
    # }
]



