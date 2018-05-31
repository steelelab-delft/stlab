# Function to write a matrix to a text file without using binary mode (np.savetxt needs binary mode)
# myfile -> Open file to write to
# mat -> Matrix to write.  Should consist of numbers that are convertible to double precision
# f -> Format specifier.  Default %.10e, exponential notation with 10 decimal places
# delim -> Delimiter separating row elements.  Rows are separated by (surprise, surprise) a newline
# blocksep -> String inserted after the matrix.  By default an extra newline '\n' for spyview blocks
import numpy as np
import os
def writematrix(myfile,mat,f='%.10e',delim=', ',blocksep='\n'):
    for line in mat:
        line = ['%.10e' % x for x in line]
        line = delim.join(line)
        myfile.write(line+'\n')
    myfile.write(blocksep)
    
def writedict(myfile,mydict,f='%.10e',delim=', ',blocksep='\n'):
    vv = list(mydict.keys())
    writetitle(myfile,vv,delim)
    mat = []
    for nn in mydict.keys():
        mat.append(mydict[nn])
    mat = np.asarray(mat)
    mat = mat.T
    writematrix(myfile,mat,f,delim,blocksep)

def writeparnames(myfile,params,delim=', '):
    myfile.write('#' + delim.join(params.keys()) + '\n')
    return

def writeparams(myfile,params,f='%.10e',delim=', '):
    line = [f % x for x in [params[label].value for label in params.keys()] ]
    myfile.write(delim.join(line) + '\n')
    return

def params_to_str(params,f='%.10e',delim=', '):
    line = [f % x for x in [params[label].value for label in params.keys()] ]
    return delim.join(line)

def writedictarray(myfile,mydictarray,f='%.10e',delim=', ',blocksep='\n'):
    vv = list(mydictarray[0].keys())
    writetitle(myfile,vv,delim)
    for block in mydictarray:
        writedict(myfile,block,f,delim,blocksep)
    return

#???
def writeline(myfile,line,f='.10e',delim=', '):
    for x in line[:-1]:
        myfile.write("{:{form}}".format(x,form = f) + delim)
    myfile.write("{:{form}}\n".format(line[-1],form = f))
    return
#???

def writeframe(myfile,myframe,f='%.10e',delim=', ',blocksep='\n'):
    vv = list(myframe)
    writetitle(myfile,vv,delim)
    mat = myframe.values
    writematrix(myfile,mat,f,delim,blocksep)

def writeframearray(myfile,myframearray,f='%.10e',delim=', ',blocksep='\n'):
    vv = list(myframearray[0])
    writetitle(myfile,vv,delim)
    for block in myframearray:
        writeframe(myfile,block,f,delim,blocksep)
    return

def writetitle(myfile,vv,delim):
    #myfile.flush()
    if myfile.tell() == 0: #Is the file new?  If so, write title line from provided data
        varline = '#' + delim.join(vv) + '\n'
        myfile.write(varline)
