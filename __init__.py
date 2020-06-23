# Loads utils with shorter names
from stlabutils.newfile import newfile #Callable as stlab.newfile(...)
import stlabutils.metagen as metagen #Callable as stlab.metagen.fromlimits(...)
import stlabutils.readdata as readdata #Callable as stlab.readdata.readQUCS(...)
from stlabutils.writematrix import savetxt #Callable as stlab.savetxt(...)
from stlabutils.writematrix import savedict
from stlabutils.writematrix import savedictarray
from stlabutils.writematrix import writeparams #Callable as stlab.savetxt(...)
from stlabutils.writematrix import writeparnames
from stlabutils.writematrix import params_to_str
from stlabutils.writematrix import writeline
from stlabutils.writematrix import saveframe
from stlabutils.writematrix import saveframearray
from stlabutils.stlabdict import stlabdict
from stlabutils.stlabdict import stlabmtx
from stlabutils.stlabdict import framearr_to_mtx
try: # some users might not need S11fit
    from stlabutils.S11fit import S11fit #Callable as stlab.S11fit(...)
    from stlabutils.S11fit import S11func #Callable as stlab.S11fit(...)
    from stlabutils.S11fit import S11back #Callable as stlab.S11fit(...)
    from stlabutils.S11fit import S11theo #Callable as stlab.S11fit(...)
except ImportError:
    print('Warning: Missing dependencies for S11fit! Fitting routines not imported.')
try: # some users might not need to do measurements
    #from stlab.devices.base_instrument import SaveInstrumentMetadata #Callable as stlab.SaveInstrumentMetadata(...)
    from .devices.autodetect_instrument import autodetect_instrument as adi #Callable as stlab.devices.adi(...)
except ImportError as e:
    print(e)
    print('Warning: Missing dependencies for autodetect_instrument! Autodetect routines not imported.')

from stlabutils.autoplotter import autoplot #Call as stlab.autoplot(...)
