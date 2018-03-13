import numpy as np

class Tank():
    def __init__(self, tank_id, current_load, max_load, consumption_rate, n_discrete_load_levels):
        self.id = tank_id
        self.load = current_load
        self.max_load = max_load
        self.rate = consumption_rate
        self.levels = np.linspace(0,self.max_load, n_discrete_load_levels+1)
   
    def fill(self):
        self.load = self.max_load    
        
    def partial_fill(self, fill_percentage):
        self.load = self.load + self.max_load * fill_percentage
    
    def tank_extra_capacity(self):
        return(self.max_load - self.load)
       
    def is_empty(self):
        if self.load <= 0:
            return(True)
        else:
            return(False)
       
    def consume(self):
        self.load = max(0, self.load - self.rate)
       
    def load_to_lvl(self):
        levels = self.levels
        #print(np.where(np.isin(levels,levels[ (levels >= self.load) ])))
        lvl = np.amin(np.where(np.isin(levels,levels[ (levels >= self.load) ])))-1
        if(lvl == -1):
            return(0)
        else:
            return(lvl)
      
    def lvl_to_load(self, lvl):
        # Warning: this could be a load different to the one the truck has, since when discretizing in levels
        # we lose information depending on how width the partition intervals are.
        if lvl == -1:
            return(0)
        else:
            return(self.levels[lvl])
        
        