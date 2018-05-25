#New base instrument class to keep track of all instantiated instruments (whether or not they inherit from instrument) for metafile generation.
import abc
import os

class base_instrument(abc.ABC):
    instrument_list = []    
    def __init__(self):
        self.instrument_list.append(self) #when instantiated, automatically added to static instrument_list

    def PrintMetadata(self): #Should show some relevant metadata on screen.  Will usually just print GetMetadataString
        print(self.GetMetadataString())

    @abc.abstractmethod  #Must be implemented in children
    def GetMetadataString(self): #Should return a string of metadata adequate to write to a file
        pass


def SaveInstrumentMetadata(myfile = None, path = './'): #Myfile should be the relevant measurement file
    if myfile:
        metapath = os.path.dirname(os.path.realpath(myfile.name))
    else:
        metapath = path        
    with open(metapath,'w') as metafile:
        for dev in base_instrument.instrument_list:
            metafile.write(dev.GetMetadataString())
            metafile.write('\n' + '*'*100 + '\n')
            metafile.write('*'*100 + '\n\n')
    return
