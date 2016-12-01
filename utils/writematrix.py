# Function to write a matrix to a text file without using binary mode (np.savetxt needs binary mode)
# myfile -> Open file to write to
# mat -> Matrix to write.  Should consist of numbers that are convertible to double precision
# f -> Format specifier.  Default %.10e, exponential notation with 10 decimal places
# delim -> Delimiter separating row elements.  Rows are separated by (surprise, surprise) a newline
# blocksep -> String inserted after the matrix.  By default an extra newline '\n' for spyview blocks
import numpy as np
def writematrix(myfile,mat,f='%.10e',delim=', ',blocksep='\n'):
    for line in mat:
        line = ['%.10e' % x for x in line]
        line = delim.join(line)
        myfile.write(line+'\n')
    myfile.write(blocksep)
    
def writedict(myfile,mydict,f='%.10e',delim=', ',blocksep='\n'):
    mat = []
    for nn in mydict.keys():
        mat.append(mydict[nn])
    mat = np.asarray(mat)
    mat = mat.T
    writematrix(myfile,mat,f,delim,blocksep)
        
