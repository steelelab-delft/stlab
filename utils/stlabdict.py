from collections import OrderedDict
import numpy as np

class stlabdict(OrderedDict):
    def __init__(self, *args, **kwargs):
            super(stlabdict, self).__init__(*args, **kwargs)
    def addparcolumn(self,colname,colval): #adds a column to 
        keys = list(self.keys())
        x = self[keys[0]]
        n = len(x)
        self[colname] = np.full(n,colval)
        return