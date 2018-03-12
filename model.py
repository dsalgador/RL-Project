import numpy as np
import math
import networkx as nx
import random

import matplotlib.pyplot as plt
from tank import Tank
from truck import Truck
import copy
    
class System():
    def __init__(self, tanks, trucks, adjacency_matrix, weights_matrix):
        self.tanks = tanks
        self.trucks = trucks
        self.graph = adjacency_matrix
        self.weights = weights_matrix
        self.k = len(trucks)
        self.n = len(tanks)
        self.s = self.state()
        self.ds = self.discrete_state()
        
        self.tanks_id = self.tank_ids()
        self.trucks_id = self.truck_ids()
        self.tanks_max_load = self.tank_max_loads()
        self.trucks_max_load = self.truck_max_loads()
        self.tanks_level = self.tank_levels()
        self.trucks_level = self.truck_levels()
        
        #
        self.actions_dim = self.n * self.k
        self.states_dim = self.n_states()
        
        #
        self.a = None
        self.da = None
        
    def get_trucks(self):
            return(self.trucks)
    
    def n_states(self):
        n_s = 1
        possible_fractions_deliverable = []
        for i,truck in enumerate(self.trucks):
               possible_fractions_deliverable.append(len(truck.fractions))
        
        #print("possible_fractions_deliverable", possible_fractions_deliverable)
        n_s = n_s * (self.n+1)**(self.k) 
        
        for i in range(self.k):
            n_s = n_s * (possible_fractions_deliverable[i])
        
        n_s = n_s * np.prod([len(self.tanks_level[i])-1 for i in range(self.n)])
        #print([self.tanks_level[i] for i in range(self.n)])
                       
        return(n_s)    
               
        
    def truck_loads(self):
        return([self.trucks[i].load for i in range(self.k)])
    
    def truck_max_loads(self):
        return([self.trucks[i].max_load for i in range(self.k)])
    
    def truck_positions(self):
        return([self.trucks[i].pos for i in range(self.k)])
    
    def truck_ids(self):
        return([self.trucks[i].id for i in range(self.k)])
    
    def truck_levels(self):
        return([self.trucks[i].levels for i in range(self.k)])
    
    
    
    
    def tank_loads(self):
        return([self.tanks[i].load for i in range(self.n)])
    
    def tank_max_loads(self):
        return([self.tanks[i].max_load for i in range(self.n)])
    
    def tank_ids(self):
        return([self.tanks[i].id for i in range(self.n)])
    
    def tank_levels(self):
        return([self.tanks[i].levels for i in range(self.n)])

    
        
    
    def state(self):
        #[ positions, truck-loads, tank-loads]
        s = [self.truck_positions(), self.truck_loads(), self.tank_loads()]
        return(s)
    
    def discrete_state(self):
        ds = [ [],[] ,[] ]
        ds[0] = self.s[0]
        
        for i, truck in enumerate(self.trucks):
            ds[1].append(truck.load_to_lvl())
            
            
        for i, tank in enumerate(self.tanks):
            ds[2].append(tank.load_to_lvl())
            
        return(ds)    
            
    
    def update_state(self):
        self.s = self.state()
        self.ds = self.discrete_state()
        
    def visualize(self, show = False):
            #s = self.state()
            index = np.arange(self.n)
            tanks_max_load = self.tanks_max_load
            tank_loads = self.tank_loads()
            tanks_id = self.tanks_id
            
            plt.bar(index, tanks_max_load, color = 'black')
            plt.bar(index, tank_loads, color = 'blue' )
            plt.xlabel('Tank id', fontsize=10)
            plt.ylabel('Current level', fontsize=10)
            plt.xticks(index, tanks_id, fontsize=10, rotation=30)
            plt.title('Current tanks state')
            
            if show:  plt.show()
            
            return([index, tanks_max_load, tank_loads, tanks_id])
        
    def visualize_step(self, args): 
            index, tanks_max_load, tank_loads, tanks_id = args;
            plt.bar(index, tanks_max_load, color = 'black')
            plt.bar(index, tank_loads, color = 'blue' )
            plt.xlabel('Tank id', fontsize=10)
            plt.ylabel('Current level', fontsize=10)
            plt.xticks(index, tanks_id, fontsize=10, rotation=30)
            plt.title('Current tanks state')
        
    
    def is_some_tank_empty(self):
        for tank in self.tanks:
            if tank.is_empty():
                return(True)
        return(False)    
    
    def reset_trucks_positions(self):
        for truck in self.trucks:
            truck.pos = 0
        
    def random_action(self, seed = None, verbose = False):
        if seed != None:
            random.seed(seed)
            
            
        new_positions = [] 
        new_deliveries = []
        new_deliveries_index = []
        
        rewards = 0  
        print("self.trucks",self.get_trucks())
            
        # Choose a position for each truck randomly
        
        #CORRE GIR EL CODIGO, PLANTEAMIENTO PARA QUE FUNCIONE
        #possible_positions_index = np.isin(self.graph, 1)
        #possible_positions = np.where(possible_positions_index)
        #print("possible_positions:", possible_positions)
        for truck in self.get_trucks():
            old_position = truck.pos
            if verbose: print("truck pos: ", old_position)
            possible_positions_index = np.isin(self.graph[old_position], 1)
            possible_positions = np.where(possible_positions_index)
            #random.randint(0,len(possible_positions[0])-1)
            if verbose: print("nº of possible positions", len(possible_positions_index))
            new_position = random.randrange(len(possible_positions_index)-1 )
            if verbose: print("new position: ",new_position)
            truck.pos = new_position
            if verbose: print("possible_positions:", possible_positions)
            
            # Update rewards due to oil costs (transport/km)
            rewards = rewards - self.weights[old_position][new_position]
            new_positions.append(new_position)

            
            
        # Choose a new (possible) load delivery for each truck to the new tank (position)
        # and update the tank's load after deliverying the chosen quantity.
        for current_truck in self.get_trucks():
                truck_pos = current_truck.pos
                if verbose: print("truck_pos: ", current_truck_pos)

                #current_truck = truck
                current_tank = self.tanks[truck_pos]
                current_extra_tank_capacity = current_tank.tank_extra_capacity()
                possible_delivery_quantities = current_truck.possible_delivery_quantities(current_extra_tank_capacity)
                if verbose: print("Possible delivery quantities: ", possible_delivery_quantities)
                if possible_delivery_quantities.size == 0:
                    if verbose: print(f"Truck {truck.id} in tank {truck.pos} does not deliver")
                else:
                    random_index = random.randint(0,len(possible_delivery_quantities)-1)
                    #delivery_quantity = np.random.choice(possible_delivery_quantities)
                    delivery_quantity = possible_delivery_quantities[random_index]
                    current_tank.load = current_tank.load + delivery_quantity
                    if verbose: print(f"Truck {truck.id} in tank {truck.pos} delivers {delivery_quantity} units")
                
                    rewards = rewards - delivery_quantity
                    new_deliveries_index.append(random_index)
                    new_deliveries.append(delivery_quantity)
                    
        #old_state = self.state()    
        
        # Update the loads of the tanks accordig to their consumption rates
        for tank in self.tanks:           
            tank.consume()
        
        #new_state = self.state()
        
        # Penalize infinitelly if some tank is empty
        if self.is_some_tank_empty():
            rewards = -np.inf
            
        self.update_state()   
        
        self.da = [new_positions, new_deliveries_index]
        self.a = [new_positions, new_deliveries]

        return(rewards)    