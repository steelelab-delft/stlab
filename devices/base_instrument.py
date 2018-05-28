#New base instrument class to keep track of all instantiated instruments (whether or not they inherit from instrument) for metafile generation.
import abc
import os
import datetime

#class base_instrument(abc.ABC):
class base_instrument():
    instrument_list = []    
    def __init__(self):
        self.instrument_list.append(self) #when instantiated, automatically added to static instrument_list

    def PrintMetadata(self): #Should show some relevant metadata on screen.  Will usually just print GetMetadataString
        print(self.GetMetadataString())

#    @abc.abstractmethod  #Must be implemented in children
    def GetMetadataString(self): #Should return a string of metadata adequate to write to a file
        if 'MetaGetters' in dir(self):
            getters = self.MetaGetters()
        else:
            getters = [method_name for method_name in dir(self)
                        if callable(getattr(self, method_name))
                        if method_name.startswith('Get') ]
            getters.remove('GetMetadataString')
        print(getters)
        pairs = []
        for method in getters:  
            method_to_call = getattr(self, method)
            pairs.append( (method,method_to_call()) )
        result = ''
        for x,y in pairs:
            result += x + ' = ' + str(y) + '\n'
        return result

# Function to save all instantiated instrument metadata to a file
def SaveInstrumentMetadata(myfile = None): #Myfile should be the relevant measurement file
    #if myfile is given, try to treat it like a measurement file handle first
    if myfile:
        try:
            metafilename,_ = os.path.splitext(myfile.name) + '.meta.dat'
        except AttributeError: #If myfile is not a file, then treat it as a string
            metafilename = myfile
    else: #if myfile is not given, make the metafile in the current folder with a timestamp
        mytime = datetime.datetime.now()
        datecode = '%s' % mytime.year + '_' + ('%s' % mytime.month).zfill(2) + '_' +('%s' % mytime.day).zfill(2)
        timecode = ('%s' % mytime.hour).zfill(2) +'.' + ('%s' % mytime.minute).zfill(2) +'.' + ('%s' % mytime.second).zfill(2)
        metafilename = './meta_' + datecode + '_' + timecode + '.dat'

    with open(metafilename,'w') as metafile:
        for dev in base_instrument.instrument_list:
            metafile.write('\n' + '*'*100 + '\n')
            metafile.write(str(dev.GetMetadataString()))
            metafile.write('*'*100 + '\n')
    return
