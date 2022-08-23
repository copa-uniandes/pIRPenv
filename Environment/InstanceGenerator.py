################################## Modules ##################################
### Basic Librarires
import numpy as np; from copy import copy, deepcopy; import matplotlib.pyplot as plt
import networkx as nx; import sys; import pandas as pd; import math; import numpy as np
import time; from termcolor import colored
from numpy.random import seed, normal, lognormal, randint

### Optimizer
import gurobipy as gu

### Renderizing
import imageio

### Gym & OR-Gym
from or_gym import utils


class instance_generator():

    def __init__(self, env, rd_seed, **kwargs):
        
        seed(rd_seed)
        
        ### Importing instance parameters ###
        self.M = env.M; self.Suppliers = env.Suppliers    # Suppliers
        self.V = env.V
        self.K = env.K; self.Products = env.Products      # Products
        self.F = env.F; self.Vehicles = env.Vehicles      # Fleet
        self.T = env.T
        self.Horizon = env.Horizon
    
        self.s_params = env.stochastic_parameters
        self.others = env.other_env_params
        
        self.W_t = {}

        if self.others['look_ahead']:
            self.S = env.S                       # Number of sample paths
            self.LA_horizon = env.LA_horizon     # Look-ahead time window's size (includes current period)
            self.sample_paths = {}
        
        ### historical log parameters ###
        if self.others['historical']:  
            self.hist_window = env.hist_window       # historical window 
            self.TW = env.TW
            self.historical = env.historical
            self.historical_data = {}
        else:
            self.TW == self.Horizon


    def gen_ages(self):
        '''
        O_k: (dict) maximum days that k \in K can be held in inventory
        '''
        # Maximum days that product k can be held in inventory before rotting
        max_age = self.T
        self.O_k = {k:randint(1,max_age) for k in self.Products}

        return self.O_k 
    

    def gen_routing_costs(self):
        '''
        c: (dict) transportation cost between nodes i \in V and j \in V
        '''
        # Suppliers locations in grid
        size_grid = 1000
        coor = {i:(randint(0, size_grid), randint(0, size_grid)) for i in self.V}

        # Transportation cost between nodes i and j, estimated using euclidean distance
        c = {(i,j):round(np.sqrt((coor[i][0]-coor[j][0])**2 + (coor[i][1]-coor[j][1])**2)) for i in self.V for j in self.V if i!=j} 

        return c


    def generate_sample_paths(self):
        pass


    def gen_h_cost(self, distribution = 'd_uniform', **kwargs):
        '''
        h_t: (dict) holding cost of k \in K on t \in T
        '''
        if distribution == 'd_uniform':
            h_t = {(k,t):randint(kwargs['min'], kwargs['max']) for k in self.Products for t in self.Horizon}

            if self.s_params != False and ('h' in self.s_params or '*' in self.s_params):
                self.W_t = {(k,t+1): randint(kwargs['min'], kwargs['max']) for k in self.Products for t in self.Horizon}
            
            if self.others['historical'] != False and ('h' in self.others['historical'] or '*' in self.others['historical']):
                self.historical_data['h'] = {k:[randint(kwargs['min'], kwargs['max']) for t in self.historical] for k in self.Products}
            
            if self.others['look_ahead'] != False and ('h' in self.others['look_ahead'] or '*' in self.others['look_ahead']):
                pass
            
        return h_t
            

    def gen_availabilities(self):
        '''
        M_kt: (dict) subset of suppliers that offer k \in K on t \in T
        K_it: (dict) subset of products offered by i \in M on t \in T
        '''
        self.M_kt = {}
        # In each time period, for each product
        for k in self.Products:
            for t in self.TW:
                # Random number of suppliers that offer k in t
                sup = randint(1, self.M + 1)
                self.M_kt[k,t] = list(self.Suppliers)
                # Random suppliers are removed from subset, regarding {sup}
                for ss in range(self.M - sup):
                    a = int(randint(0, len(self.M_kt[k,t])))
                    del self.M_kt[k,t][a]
        
        # Products offered by each supplier on each time period, based on M_kt
        self.K_it = {(i,t):[k for k in self.Products if i in self.M_kt[k,t]] for i in self.Suppliers for t in self.TW}

        return self.M_kt, self.K_it 


    def gen_quantities(self, distribution = 'normal', **kwargs):
        self.q_t = {}

        if distribution == 'normal':
            self.historical_data['q'] = {(i,k): [normal(kwargs['mean'], kwargs['stdev']) if i in self.M_kt[k,t] else 0 for t in self.historical] for i in self.Suppliers for k in self.Products}
            self.q_t = {(i,k,t):normal(kwargs['mean'], kwargs['stdev']) if i in self.M_kt[k,t] else 0 for i in self.Suppliers for k in self.Products for t in self.Horizon}
        elif distribution == 'log-normal':
            self.historical_data['q'] = {(i,k): [lognormal(kwargs['mean'], kwargs['stdev']) if i in self.M_kt[k,t] else 0 for t in self.historical] for i in self.Suppliers for k in self.Products}
            self.q_t = {(i,k,t): lognormal(kwargs['mean'], kwargs['stdev']) if i in self.M_kt[k,t] else 0 for i in self.Suppliers for k in self.Products for t in self.Horizon}
        elif distribution == 'uniform':
            self.historical_data['q'] = {(i,k): [randint(kwargs['min'], kwargs['max']) if i in self.M_kt[k,t] else 0 for t in self.historical] for i in self.Suppliers for k in self.Products}
            self.q_t = {(i,k,t): randint(kwargs['min'], kwargs['max']) if i in self.M_kt[k,t] else 0 for i in self.Suppliers for k in self.Products for t in self.Horizon}
    

    def gen_demand(self, distribution = 'normal', **kwargs):
        self.d_t = {}

        if distribution == 'normal':
            self.historical_data['d'] = {(k):[normal(kwargs['mean'], kwargs['stdev']) for t in self.historical] for k in self.Products}
            self.d_t = {(k,t): normal(kwargs['mean'], kwargs['stdev']) for k in self.Products for t in self.Horizon}
        elif distribution == 'log-normal':
            self.historical_data['d'] = {(k):[lognormal(kwargs['mean'], kwargs['stdev']) for t in self.historical] for k in self.Products}
            self.d_t = {(k,t): lognormal(kwargs['mean'], kwargs['stdev']) for k in self.Products for t in self.Horizon}
        elif distribution == 'uniform':
            self.historical_data['d'] = {(k):[randint(kwargs['min'], kwargs['max']) for t in self.historical] for k in self.Products}
            self.d_t = {(k,t): randint(kwargs['min'], kwargs['max']) for k in self.Products for t in self.Horizon}


    def gen_p_price(self, distribution = 'normal', **kwargs):
        self.p_t = {}
        
        if distribution == 'normal':
            self.historical_data['p'] = {(i,k): [normal(kwargs['mean'], kwargs['stdev']) if i in self.M_kt[k,t] else 1000 for t in self.historical] for i in self.Suppliers for k in self.Products for t in self.historical}
            self.p_t = {(i,k,t): normal(kwargs['mean'], kwargs['stdev']) if i in self.M_kt[k,t] else 1000 for i in self.Suppliers for k in self.Products for t in self.Horizon}
        elif distribution == 'log-normal':
            self.historical_data['p'] = {(i,k): [lognormal(kwargs['mean'], kwargs['stdev']) if i in self.M_kt[k,t] else 1000 for t in self.historical] for i in self.Suppliers for k in self.Products for t in self.historical}
            self.p_t = {(i,k,t):lognormal(kwargs['mean'], kwargs['stdev']) if i in self.M_kt[k,t] else 1000 for i in self.Suppliers for k in self.Products for t in self.Horizon}
        elif distribution == 'uniform':
            self.historical_data['p'] = {(i,k): [randint(kwargs['min'], kwargs['max']) if i in self.M_kt[k,t] else 1000 for t in self.historical] for i in self.Suppliers for k in self.Products for t in self.historical}
            self.p_t = {(i,k,t): randint(kwargs['min'], kwargs['max']) if i in self.M_kt[k,t] else 1000 for i in self.Suppliers for k in self.Products for t in self.Horizon}
    

    def gen_h_price(self, distribution = 'normal', **kwargs):
        self.h_t = {}

        if distribution == 'normal':
            self.historical_data['h'] = {k: [normal(kwargs['mean'], kwargs['stdev']) for t in self.historical] for k in self.Products}
            self.h_t = {(k,t): normal(kwargs['mean'], kwargs['stdev']) for k in self.Products for t in self.Horizon}
        elif distribution == 'log-normal':
            self.historical_data['h'] = {k: [lognormal(kwargs['mean'], kwargs['stdev']) for t in self.historical] for k in self.Products}
            self.h_t = {(k,t): lognormal(kwargs['mean'], kwargs['stdev']) for k in self.Products for t in self.Horizon}
        elif distribution == 'uniform':
            self.historical_data['h'] = {k: [randint(kwargs['min'], kwargs['max']) for t in self.historical] for k in self.Products}
            self.h_t = {(k,t): randint(kwargs['min'], kwargs['max']) for k in self.Products for t in self.Horizon}
    

    def conf_int_gen(self, **kwargs):

        self.gen_availabilities()
        self.gen_quantities(**kwargs['q'])
        self.gen_demand(**kwargs['d'])
        self.gen_p_price(**kwargs['p'])
        self.gen_h_price(**kwargs['h'])


    

    