"""Signal Analyzer testing script

Script used to test Signal Analyzer behavior with operations that should be common
to all Signal Analyzers

"""

# Signal Analyzer baseclass testing

import stlab

## Communication

FSV = stlab.adi('TCPIP::192.168.1.114::INSTR')
EXA = stlab.adi('K-N9010B-60854')

## Initializing

FSV.SetPoints(2001)
FSV.SetVideoBW(30)
FSV.SetResolutionBW(5)
FSV.SetAveragesType('POW')
FSV.SetAverages(21)
FSV.SetTraceAverageOn()
FSV.SetCenter(7.56e9)
FSV.SetSpan(6.5e3)
FSV.DisplayOn()
FSV.SetReference('EXT')

EXA.SetPoints(2001)
EXA.SetVideoBW(30)
EXA.SetResolutionBW(5)
EXA.SetAveragesType('POW')
EXA.SetAverages(21)
EXA.SetTraceAverageOn()
EXA.SetCenter(7.56e9)
EXA.SetSpan(6.5e3)
EXA.DisplayOn()
EXA.SetReference('EXT')

## Measurement

dataFSV = FSV.MeasureScreen()
print(dataFSV)

dataEXA = EXA.MeasureScreen()
print(dataEXA)

## Plotting

import matplotlib.pyplot as plt

plt.plot(dataFSV['Frequency (Hz)'], dataFSV['Spectrum (dBm)'])
plt.show()
plt.close()

plt.plot(dataEXA['Frequency (Hz)'], dataEXA['Spectrum (dBm)'])
plt.show()
plt.close()

## Shutdown

FSV.close()
EXA.close()