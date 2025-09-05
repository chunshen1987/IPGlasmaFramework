#!/usr/bin/env python3
"""
    This script translates the posterior chain files in the parameters
    can be read in by the iEBE-MUSIC package.
"""

import pickle
import sys

parameterName = [
    "m", "BG", "BGq", "useConstituentQuarkProton", "smearingWidth",
    "QsmuRatio", "m_jimwlk", "Lambda_QCD_jimwlk"
]

try:
    setId = int(sys.argv[1])
    setFlag = int(sys.argv[2])
    paramFile = str(sys.argv[3])
except:
    print("Usage: parameterGenerator.py <setId> <setFlag> <paramFile>")
    sys.exit(1)

with open("chain.pkl", 'rb') as f:
    data = pickle.load(f)

setName = 'chain'

nParamSets = data[setName].shape[0]
setId = setId % nParamSets
paramSet = data[setName][setId, :]
print(f"Using parameter set: {setId} from {setName}")
paramDict = {}
for i, param_i in enumerate(parameterName):
    paramDict[param_i] = paramSet[i]
paramDict['UVdamp'] = 0.
paramDict['omega'] = 1.
paramDict['Kfactor'] = 1.

with open(paramFile, "w") as f:
    for key_i in paramDict.keys():
        f.write("{}  {}\n".format(key_i, paramDict[key_i]))
