"""
@author: juanbeta
Independent transition blocks of a Supply Chain
"""
################################## Modules ##################################
### Basic Librarires
from numpy.random import seed, random, randint, lognormal
from copy import deepcopy
from termcolor import colored

class Routing_management():

    def __init__(self):
        pass
    
    def evaluate_routes(inst_gen, routes):
        transport_cost = 0
        for route in routes:
            transport_cost += sum(inst_gen.c[route[i], route[i + 1]] for i in range(len(route) - 1))
        return transport_cost


class Inventory_management():
    
    class perish_per_age_inv():

        def reset(inst_gen):
            ## State ##

            state = {(k,o):inst_gen.i00[k,o]  for k in inst_gen.Products for o in range(1, inst_gen.O_k[k] + 1)}
            if inst_gen.other_params['backorders'] == 'backlogs':
                for k in inst_gen.Products:
                    state[k,'B'] = 0
            
            return state
    
        def get_real_dem_compl_FIFO(inst_gen, env, real_purchase):
            real_demand_compliance={}
            for k in inst_gen.Products:
                left_to_comply = inst_gen.W_d[env.t][k]
                for o in range(inst_gen.O_k[k],0,-1):
                    real_demand_compliance[k,o] = min(env.state[k,o], left_to_comply)
                    left_to_comply -= real_demand_compliance[k,o]
                
                real_demand_compliance[k,0] = min(sum(real_purchase[i,k] for i in inst_gen.Suppliers), left_to_comply)
            
            return real_demand_compliance

        def get_real_dem_compl_rate(inst_gen, env, rates, real_purchase, strong_rate):
            
            if strong_rate: rates = {(a):int(rates[a]) for a in rates}

            real_demand_compliance = {}
            for k in inst_gen.Products:
                left_to_comply = inst_gen.W_d[env.t][k]
                real_demand_compliance[k,0] = min(rates[k,0]*sum(real_purchase[i,k] for i in inst_gen.Suppliers), left_to_comply)
                left_to_comply -= real_demand_compliance[k,0]
                for o in range(inst_gen.O_k[k],0,-1):
                    real_demand_compliance[k,o] = min(rates[k,o]*env.state[k,o], left_to_comply)
                    left_to_comply = max(0,left_to_comply-real_demand_compliance[k,o])
            
            return real_demand_compliance

        def get_real_dem_age_compl_rate(inst_gen, env, rates, real_purchase, strong_rate):
            
            if strong_rate: rates = {(a):int(rates[a]) for a in rates}

            real_demand_compliance = {}
            for k in inst_gen.Products:
                left_to_comply = inst_gen.W_d[env.t][k,0]
                real_demand_compliance[k,0] = min(rates[k,0]*sum(real_purchase[i,k] for i in inst_gen.Suppliers), left_to_comply)
                for o in range(1,inst_gen.O_k[k]+1):
                    left_to_comply = inst_gen.W_d[env.t][k,o]
                    real_demand_compliance[k,o] = min(rates[k,o]*env.state[k,o], left_to_comply)
            
            return real_demand_compliance

        def update_inventory(inst_gen, env, purchase, demand_compliance, warnings, back_o_compliance = False):
            inventory = deepcopy(env.state)
            back_orders = {}
            perished = {}

            # Inventory update
            for k in inst_gen.Products:
                inventory[k,1] = round(sum(purchase[i,k] for i in inst_gen.Suppliers) - demand_compliance[k,0],2)

                max_age = inst_gen.O_k[k]
                if max_age > 1:
                    for o in range(2, max_age + 1):
                            inventory[k,o] = round(env.state[k,o - 1] - demand_compliance[k,o - 1],2)
                
                if inst_gen.other_params['backorders'] == 'backorders' and sum(demand_compliance[k,o] for o in range(inst_gen.O_k[k] + 1)) < inst_gen.W_d[env.t][k]:
                    back_orders[k] = round(inst_gen.W_d[env.t][k] - sum(demand_compliance[k,o] for o in range(inst_gen.O_k[k] + 1)),2)

                if inst_gen.other_params['backorders'] == 'backlogs':
                    new_backlogs = round(max(inst_gen.W_d[k] - sum(demand_compliance[k,o] for o in range(inst_gen.O_k[k] + 1)),0),2)
                    inventory[k,'B'] = round(env.state[k,'B'] + new_backlogs - sum(back_o_compliance[k,o] for o in range(inst_gen.O_k[k]+1)),2)
                
                if env.state[k, max_age] - demand_compliance[k,max_age] > 0:
                        perished[k] = env.state[k, max_age] - demand_compliance[k,max_age]
        

                # Factibility checks         
                if warnings:
                    if env.state[k, max_age] - demand_compliance[k,max_age] > 0:
                        # reward += self.penalization_cost
                        print(colored(f'Warning! {env.state[k, max_age] - demand_compliance[k,max_age]} units of {k} were lost due to perishability','yellow'))
        

                    if sum(demand_compliance[k,o] for o in range(inst_gen.O_k[k] + 1)) < inst_gen.W_d[env.t][k]:
                        print(colored(f'Warning! Demand of product {k} was not fulfilled', 'yellow'))

            return inventory, back_orders, perished
        
        def update_inventory_age(inst_gen, env, purchase, demand_compliance, warnings, back_o_compliance = False):
            inventory = deepcopy(env.state)
            back_orders = {}
            perished = {}

            # Inventory update
            for k in inst_gen.Products:
                inventory[k,1] = round(sum(purchase[i,k] for i in inst_gen.Suppliers) - demand_compliance[k,0],2)

                max_age = inst_gen.O_k[k]
                if max_age > 1:
                    for o in range(2, max_age + 1):
                            inventory[k,o] = round(env.state[k,o - 1] - demand_compliance[k,o - 1],2)
                
                if inst_gen.other_params['backorders'] == 'backorders':
                    for o in range(inst_gen.O_k[k]+1):
                        if demand_compliance[k,o] < inst_gen.W_d[env.t][k,o]:
                            back_orders[k,o] = round(inst_gen.W_d[env.t][k,o] - demand_compliance[k,o],2)
                        else:
                            back_orders[k,o] = 0

                if inst_gen.other_params['backorders'] == 'backlogs':
                    new_backlogs = round(max(inst_gen.W_d[k,o] - sum(demand_compliance[k,o] for o in range(inst_gen.O_k[k] + 1)),0),2)
                    inventory[k,'B'] = round(env.state[k,'B'] + new_backlogs - sum(back_o_compliance[k,o] for o in range(inst_gen.O_k[k]+1)),2)
                
                if env.state[k, max_age] - demand_compliance[k,max_age] > 0:
                        perished[k] = env.state[k, max_age] - demand_compliance[k,max_age]

            return inventory, back_orders, perished

        def compute_costs(inst_gen, env, purchase, demand_compliance, s_tprime, perished):            
            purchase_cost = sum(purchase[i,k] * inst_gen.W_p[env.t][i,k]   for i in inst_gen.Suppliers for k in inst_gen.Products)
        
            holding_cost = sum(sum(s_tprime[k,o] for o in range(1, inst_gen.O_k[k] + 1)) * inst_gen.W_h[env.t][k] for k in inst_gen.Products)
            for k in perished.keys():
                holding_cost += perished[k] * inst_gen.W_h[env.t][k]

            backorders_cost = 0
            if inst_gen.other_params['backorders'] == 'backorders':
                backorders = sum(max(inst_gen.W_d[env.t][k] - sum(demand_compliance[k,o] for o in range(inst_gen.O_k[k]+1)),0) for k in inst_gen.Products)
                backorders_cost = backorders * inst_gen.back_o_cost
            
            elif inst_gen.other_params['backorders'] == 'backlogs':
                backorders_cost = sum(s_tprime[k,'B'] for k in inst_gen.Products) * inst_gen.back_l_cost

            return purchase_cost, holding_cost, backorders_cost
        
        def compute_earnings(inst_gen, demand_compliance):
            earnings = sum(inst_gen.sell_prices[k,o]*demand_compliance[k,o] for k in inst_gen.Products for o in range(inst_gen.O_k[k]+1))
        
            return earnings

        def compute_costs_age(inst_gen, env, purchase, demand_compliance, s_tprime, perished):            
            purchase_cost = sum(purchase[i,k] * inst_gen.W_p[env.t][i,k]   for i in inst_gen.Suppliers for k in inst_gen.Products)
        
            holding_cost = sum(sum(s_tprime[k,o] for o in range(1, inst_gen.O_k[k] + 1)) * inst_gen.W_h[env.t][k] for k in inst_gen.Products)
            
            for k in perished.keys():
                holding_cost += perished[k] * inst_gen.W_h[env.t][k]

            backorders_cost = 0
            if inst_gen.other_params['backorders'] == 'backorders':
                backorders = sum(inst_gen.W_d[env.t][k,o]-demand_compliance[k,o] for k in inst_gen.Products for o in range(inst_gen.O_k[k]+1))
                backorders_cost = backorders * inst_gen.back_o_cost
            
            elif inst_gen.other_params['backorders'] == 'backlogs':
                backorders_cost = sum(s_tprime[k,'B'] for k in inst_gen.Products) * inst_gen.back_l_cost

            return purchase_cost, holding_cost, backorders_cost