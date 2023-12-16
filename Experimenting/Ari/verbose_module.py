import numpy as np
from pickle import dump, load
import os

class headers():

    @staticmethod
    def print_simple_header(w):
        print("\n---------------------------------------------------------------------------------------------------------------------------------------")
        print(" "*int(np.floor((135-len(w)-11)/2)) + f"Optimizing {w}" + " "*int(np.ceil((135-len(w)-11)/2)))
        print("---------------------------------------------------------------------------------------------------------------------------------------")
    
    @staticmethod
    def print_header(s):
        print("\n------------------------------------------------------")
        print(" "*int(np.floor((54-len(s))/2)) + s + " "*int(np.ceil((54-len(s))/2))  )
        print("------------------------------------------------------\n")

class objectives_performance():

    @staticmethod
    def show_normalization(inst_gen,env):

        print("\t"+" "*8,*[" "*int(np.floor((15-len(e))/2))+e+" "*int(np.ceil((15-len(e))/2))+"\t" for e in ["costs"]+inst_gen.E],sep="\t")
        for e in ["costs"]+inst_gen.E:
            print("\t"+e+"*"+" "*(8-len(e)-1),*[f"{env.payoff_matrix[e][ee]:.2e}" + f" ({(env.payoff_matrix[e][ee]-env.norm_matrix[ee]['best'])/(env.norm_matrix[ee]['worst']-env.norm_matrix[ee]['best']):.2f}) " for ee in ["costs"]+inst_gen.E],sep="\t")
    
    @staticmethod
    def show_balanced_solution(inst_gen,env,la_decisions):
        
        inventory, purchase, backorders, flow_x, flow_y = la_decisions[0], la_decisions[1], la_decisions[2], la_decisions[4], la_decisions[5]; impact = dict()

        purch_cost = sum(inst_gen.W_p[env.t][i,k]*purchase[t][s][i,k] for t in purchase for s in inst_gen.Samples for k in inst_gen.Products for i in inst_gen.M_kt[k,env.t + t])/len(inst_gen.Samples)
        backo_cost = sum(inst_gen.back_o_cost[k]*backorders[t][s][k] for t in backorders for s in inst_gen.Samples for k in inst_gen.Products)/len(inst_gen.Samples)
        rout_cost = sum(inst_gen.c[i,j]*flow_x[t][s][i,j] for (i,j) in inst_gen.A for t in flow_x for s in inst_gen.Samples)/len(inst_gen.Samples)
        holding_cost = sum(inst_gen.W_h[t][k]*inventory[t][s][k,o] for t in inventory for s in inst_gen.Samples for k in inst_gen.Products for o in range(inst_gen.O_k[k]))/len(inst_gen.Samples)
        if inst_gen.hold_cost: impact["costs"] = purch_cost + backo_cost + rout_cost + holding_cost
        else: impact["costs"] = purch_cost + backo_cost + rout_cost
        
        for e in inst_gen.E:
            transport = sum(inst_gen.c_LCA[e][k][i,j]*flow_y[t][s][i,j,k] for t in purchase for s in inst_gen.Samples for k in inst_gen.Products for (i,j) in inst_gen.A)/len(inst_gen.Samples)
            storage = sum(inst_gen.h_LCA[e][k]*inventory[t][s][k,o] for t in inventory for s in inst_gen.Samples for k in inst_gen.Products for o in range(inst_gen.O_k[k]))/len(inst_gen.Samples)
            waste = sum(inst_gen.waste_LCA[e][k]*inventory[t][s][k,inst_gen.O_k[k]] for k in inst_gen.Products for t in inventory for s in inst_gen.Samples)/len(inst_gen.Samples)

            impact[e] = transport + storage + waste

        print("\n\t"+" "*8,*[" "*int(np.floor((15-len(e))/2))+e+" "*int(np.ceil((15-len(e))/2))+"\t" for e in ["costs"]+inst_gen.E],sep="\t")
        print("\tresults ",*[f"{impact[e]:.2e}" + f" ({(impact[e]-env.norm_matrix[e]['best'])/(env.norm_matrix[e]['worst']-env.norm_matrix[e]['best']):.2f}) " for e in ["costs"]+inst_gen.E],sep="\t")


class export_results():

    @staticmethod
    def export_rewards(weights,seed_ix,rewards, other_path=False, theta=1.0, gamma=1.0, min_q=0.1):

        path = "C:/Users/ari_r/" if not other_path else "C:/Users/a.rojasa55/"
        new_dir = path + f"OneDrive - Universidad de los andes/1. MIIND/Tesis/Experimentos/Service_Level_{theta}/Gamma_{gamma}/Min_q{min_q}/Rewards/Rewards_{weights}/"

        if not os.path.exists(new_dir): os.makedirs(new_dir)

        file = open(new_dir+f"Rewards_{weights}_{seed_ix}","wb")
        dump(rewards,file); file.close()
    
    @staticmethod
    def export_actions(weights,seed_ix,action, other_path=False, theta=1.0, gamma=1.0, min_q=0.1):

        path = "C:/Users/ari_r/" if not other_path else "C:/Users/a.rojasa55/"
        new_dir = path + f"OneDrive - Universidad de los andes/1. MIIND/Tesis/Experimentos/Service_Level_{theta}/Gamma_{gamma}/Min_q{min_q}/Actions/Actions_{weights}/"

        if not os.path.exists(new_dir): os.makedirs(new_dir)

        file = open(new_dir+f"Actions_{weights}_{seed_ix}","wb")
        dump(action,file); file.close()
    
    @staticmethod
    def export_lookahead_decisions(weights,seed_ix,lookahead, other_path=False, theta=1.0, gamma=1.0, min_q=0.1):

        path = "C:/Users/ari_r/" if not other_path else "C:/Users/a.rojasa55/"
        new_dir = path + f"OneDrive - Universidad de los andes/1. MIIND/Tesis/Experimentos/Service_Level_{theta}/Gamma_{gamma}/Min_q{min_q}/Lookahead/Lookahead_{weights}/"

        if not os.path.exists(new_dir): os.makedirs(new_dir)

        file = open(new_dir+f"Lookahead_{weights}_{seed_ix}","wb")
        dump(lookahead,file); file.close()
    
    @staticmethod
    def export_instance_parameters(weights,seed_ix,inst_gen, other_path=False, theta=1.0, gamma=1.0, min_q=0.1):

        path = "C:/Users/ari_r/" if not other_path else "C:/Users/a.rojasa55/"
        new_dir = path + f"OneDrive - Universidad de los andes/1. MIIND/Tesis/Experimentos/Service_Level_{theta}/Gamma_{gamma}/Min_q{min_q}/Instance/Instance_{weights}/"

        if not os.path.exists(new_dir): os.makedirs(new_dir)

        file = open(new_dir+f"Instance_{weights}_{seed_ix}","wb")
        dump(inst_gen,file); file.close()

    @staticmethod
    def export_inventory(weights, seed_ix, i0, other_path=False, theta=1.0, gamma=1.0, min_q=0.1):

        path = "C:/Users/ari_r/" if not other_path else "C:/Users/a.rojasa55/"
        new_dir = path + f"OneDrive - Universidad de los andes/1. MIIND/Tesis/Experimentos/Service_Level_{theta}/Gamma_{gamma}/Min_q{min_q}/Inventory/Inventory_{weights}/"

        if not os.path.exists(new_dir): os.makedirs(new_dir)

        file = open(new_dir+f"Inventory_{weights}_{seed_ix}","wb")
        dump(i0,file); file.close()
    
    @staticmethod
    def export_backorders(weights, seed_ix, backo, other_path=False, theta=1.0, gamma=1.0, min_q=0.1):

        path = "C:/Users/ari_r/" if not other_path else "C:/Users/a.rojasa55/"
        new_dir = path + f"OneDrive - Universidad de los andes/1. MIIND/Tesis/Experimentos/Service_Level_{theta}/Gamma_{gamma}/Min_q{min_q}/Backorders/Backorders_{weights}/"

        if not os.path.exists(new_dir): os.makedirs(new_dir)

        file = open(new_dir+f"Backorders_{weights}_{seed_ix}","wb")
        dump(backo,file); file.close()
    
    @staticmethod
    def export_perished(weights, seed_ix, perished, other_path=False, theta=1.0, gamma=1.0, min_q=0.1):

        path = "C:/Users/ari_r/" if not other_path else "C:/Users/a.rojasa55/"
        new_dir = path + f"OneDrive - Universidad de los andes/1. MIIND/Tesis/Experimentos/Service_Level_{theta}/Gamma_{gamma}/Min_q{min_q}/Perished/Perished_{weights}/"

        if not os.path.exists(new_dir): os.makedirs(new_dir)

        file = open(new_dir+f"Perished_{weights}_{seed_ix}","wb")
        dump(perished,file); file.close()
    
    @staticmethod
    def export_norm_matrix(weights, seed_ix, norm_matrix, other_path=False, theta=1.0, gamma=1.0, min_q=0.1):

        path = "C:/Users/ari_r/" if not other_path else "C:/Users/a.rojasa55/"
        new_dir = path + f"OneDrive - Universidad de los andes/1. MIIND/Tesis/Experimentos/Service_Level_{theta}/Gamma_{gamma}/Min_q{min_q}/Matrix/Matrix_{weights}/"

        if not os.path.exists(new_dir): os.makedirs(new_dir)

        file = open(new_dir+f"Matrix_{weights}_{seed_ix}","wb")
        dump(norm_matrix,file); file.close()

class import_results():

    @staticmethod
    def import_rewards(weights,seed_ix, other_path=False, theta=1.0, gamma=1.0, min_q=0.1):

        path = "C:/Users/ari_r/" if not other_path else "C:/Users/a.rojasa55/"
        new_dir = path + f"OneDrive - Universidad de los andes/1. MIIND/Tesis/Experimentos/Service_Level_{theta}/Gamma_{gamma}/Min_q{min_q}/Rewards/Rewards_{weights}/"

        file = open(new_dir+f"Rewards_{weights}_{seed_ix}","rb")
        resp = load(file); file.close()

        return resp
    
    @staticmethod
    def import_actions(weights,seed_ix, other_path=False, theta=1.0, gamma=1.0, min_q=0.1):

        path = "C:/Users/ari_r/" if not other_path else "C:/Users/a.rojasa55/"
        new_dir = path + f"OneDrive - Universidad de los andes/1. MIIND/Tesis/Experimentos/Service_Level_{theta}/Gamma_{gamma}/Min_q{min_q}/Actions/Actions_{weights}/"

        file = open(new_dir+f"Actions_{weights}_{seed_ix}","rb")
        resp = load(file); file.close()

        return resp
    
    @staticmethod
    def import_lookahead_decisions(weights,seed_ix, other_path=False, theta=1.0, gamma=1.0, min_q=0.1):

        path = "C:/Users/ari_r/" if not other_path else "C:/Users/a.rojasa55/"
        new_dir = path + f"OneDrive - Universidad de los andes/1. MIIND/Tesis/Experimentos/Service_Level_{theta}/Gamma_{gamma}/Min_q{min_q}/Lookahead/Lookahead_{weights}/"

        file = open(new_dir+f"Lookahead_{weights}_{seed_ix}","rb")
        resp = load(file); file.close()

        return resp
    
    @staticmethod
    def import_instance_parameters(weights,seed_ix, other_path=False, theta=1.0, gamma=1.0, min_q=0.1):

        path = "C:/Users/ari_r/" if not other_path else "C:/Users/a.rojasa55/"
        new_dir = path + f"OneDrive - Universidad de los andes/1. MIIND/Tesis/Experimentos/Service_Level_{theta}/Gamma_{gamma}/Min_q{min_q}/Instance/Instance_{weights}/"

        file = open(new_dir+f"Instance_{weights}_{seed_ix}","rb")
        resp = load(file); file.close()

        return resp

    @staticmethod
    def import_inventory(weights, seed_ix, other_path=False, theta=1.0, gamma=1.0, min_q=0.1):

        path = "C:/Users/ari_r/" if not other_path else "C:/Users/a.rojasa55/"
        new_dir = path + f"OneDrive - Universidad de los andes/1. MIIND/Tesis/Experimentos/Service_Level_{theta}/Gamma_{gamma}/Min_q{min_q}/Inventory/Inventory_{weights}/"

        file = open(new_dir+f"Inventory_{weights}_{seed_ix}","rb")
        resp = load(file); file.close()

        return resp
    
    @staticmethod
    def import_backorders(weights, seed_ix, other_path=False, theta=1.0, gamma=1.0, min_q=0.1):

        path = "C:/Users/ari_r/" if not other_path else "C:/Users/a.rojasa55/"
        new_dir = path + f"OneDrive - Universidad de los andes/1. MIIND/Tesis/Experimentos/Service_Level_{theta}/Gamma_{gamma}/Min_q{min_q}/Backorders/Backorders_{weights}/"

        file = open(new_dir+f"Backorders_{weights}_{seed_ix}","rb")
        resp = load(file); file.close()

        return resp
    
    @staticmethod
    def import_perished(weights, seed_ix, other_path=False, theta=1.0, gamma=1.0, min_q=0.1):

        path = "C:/Users/ari_r/" if not other_path else "C:/Users/a.rojasa55/"
        new_dir = path + f"OneDrive - Universidad de los andes/1. MIIND/Tesis/Experimentos/Service_Level_{theta}/Gamma_{gamma}/Min_q{min_q}/Perished/Perished_{weights}/"

        file = open(new_dir+f"Perished_{weights}_{seed_ix}","rb")
        resp = load(file); file.close()

        return resp

    @staticmethod
    def import_norm_matrix(weights, seed_ix, other_path=False, theta=1.0, gamma=1.0, min_q=0.1):

        path = "C:/Users/ari_r/" if not other_path else "C:/Users/a.rojasa55/"
        new_dir = path + f"OneDrive - Universidad de los andes/1. MIIND/Tesis/Experimentos/Service_Level_{theta}/Gamma_{gamma}/Min_q{min_q}/Matrix/Matrix_{weights}/"

        file = open(new_dir+f"Matrix_{weights}_{seed_ix}","rb")
        resp = load(file); file.close()

        return resp