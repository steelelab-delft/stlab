#Loads utils with shorter names
from stlab.utils.newfile import newfile #Callable as stlab.newfile(...)
import stlab.utils.metagen as metagen #Callable as stlab.metagen.fromlimits(...)
from stlab.utils.S11fit import fit as S11fit #Callable as stlab.S11fit(...)
from stlab.utils.S11fit import S11full as S11func #Callable as stlab.S11fit(...)
from stlab.utils.S11fit import backmodel as S11back #Callable as stlab.S11fit(...)
from stlab.utils.S11fit import S11theo #Callable as stlab.S11fit(...)
import stlab.utils.readdata as readdata #Callable as stlab.readdata.readQUCS(...)
from stlab.utils.writematrix import writematrix as savetxt #Callable as stlab.savetxt(...)
from stlab.utils.writematrix import writedict as savedict
