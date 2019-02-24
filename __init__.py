# Loads utils with shorter names
from stlab.utils.newfile import newfile #Callable as stlab.newfile(...)
import stlab.utils.metagen as metagen #Callable as stlab.metagen.fromlimits(...)
import stlab.utils.readdata as readdata #Callable as stlab.readdata.readQUCS(...)
from stlab.utils.writematrix import writematrix as savetxt #Callable as stlab.savetxt(...)
from stlab.utils.writematrix import writedict as savedict
from stlab.utils.writematrix import writedictarray as savedictarray
from stlab.utils.writematrix import writeparams as writeparams #Callable as stlab.savetxt(...)
from stlab.utils.writematrix import writeparnames as writeparnames
from stlab.utils.writematrix import params_to_str as params_to_str
from stlab.utils.writematrix import writeline as writeline
from stlab.utils.writematrix import writeframe as saveframe
from stlab.utils.writematrix import writeframearray as saveframearray
from stlab.utils.stlabdict import stlabdict
from stlab.utils.stlabdict import stlabmtx
from stlab.utils.stlabdict import framearr_to_mtx
try: # some users might not need S11fit
    from stlab.utils.S11fit import fit as S11fit #Callable as stlab.S11fit(...)
    from stlab.utils.S11fit import S11full as S11func #Callable as stlab.S11fit(...)
    from stlab.utils.S11fit import backmodel as S11back #Callable as stlab.S11fit(...)
    from stlab.utils.S11fit import S11theo as S11theo #Callable as stlab.S11fit(...)
except ImportError:
    print('Warning: Missing dependencies for S11fit! Fitting routines not imported.')
try: # some users might not need to do measurements
    #from stlab.devices.base_instrument import SaveInstrumentMetadata #Callable as stlab.SaveInstrumentMetadata(...)
    from stlab.devices.autodetect_instrument import autodetect_instrument as adi #Callable as stlab.devices.adi(...)
except ImportError:
    print('Warning: Missing dependencies for autodetect_instrument! Autodetect routines not imported.')

from stlab.utils.autoplotter import autoplot #Call as stlab.autoplot(...)
