#!/usr/bin/env python3

import argparse
import collections
import re
import os
import math
import numpy as np
#import matplotlib.pyplot as pl
from scipy import interpolate
hbarc=0.197327053
# the incoherent H1 data  (<W>=75 GeV)
t_data_incoherent=np.array([0.1,0.29,0.52,0.78,1.12,1.55,2.21,3.3,5.71])
dsigmadt_data_incoherent=np.array([47.3,43.8,36.7,27.8,16.8,10.05,6.04,2.8,0.875])
dsigmadt_data_incoherent_error=np.array([6.7,6.0,5.1,4.2,2.59,1.56,0.68,0.38,0.178])

# input the coherent H1 data  (<W>=75 GeV)
t_data_coherent=np.array([0.02,0.08,0.14,0.21,0.3,0.41,0.58,0.9])
dsigmadt_data_coherent=np.array([336.0,240.5,161.2,111.4,70.4,41.2,18.0,4.83])
dsigmadt_data_coherent_error=np.array([18.4,12.9,9.3,7.0,5.1,3.7,2.74,1.75])

realpart=[]
imagpart=[]
cc=0
filefolder=os.listdir('imag/')
for kk in range(len(filefolder)):
      try:
        tmprealpart=np.loadtxt("real/{}".format(filefolder[kk]))
      except OSError as e:
        zzz=0
        continue
      else:
        tmpimagpart=np.loadtxt("imag/{}".format(filefolder[kk]))
        try:
          rss=(tmprealpart.T[1])
        except IndexError as e:
          zz=0
        else:
          try:
            iss=(tmpimagpart.T[1])
          except IndexError as e:
            zz=0
          else:
            try:
              LL=len(rss)*len(iss)
            except TypeError as e:
              zz=0
            else:
              print(LL)
              if(LL>624):
                cc=cc+1
                mt=tmprealpart[:,0]
                realpart.append(tmprealpart.T[1])
                imagpart.append(tmpimagpart.T[1])
realpart = np.array(realpart)
imagpart = np.array(imagpart)

meansquare = (np.square(np.mean(realpart,axis=0)) + np.square(np.mean(imagpart,axis=0)))/(16.0*np.pi)
squaremean = (np.mean(np.square(realpart),axis=0) + np.mean(np.square(imagpart),axis=0))/(16.0*np.pi)
coherent=meansquare*1e7*hbarc*hbarc*1.43
incoherent=(squaremean-meansquare)*1e7*hbarc*hbarc*1.43
model_result=[]

# interpolate the model to the x-axis, t, values shown in the H1 data 
# the incoherent cross section
x=mt
y=incoherent
y=np.log(y+1e-20)
f=interpolate.interp1d(x,y,kind="cubic")
TT=t_data_incoherent[0:7]# only consider 0-2.5 GeV 
pion_data=f(TT)
pion_data=np.exp(pion_data)-1e-20
for kk in range(len(TT)):
    model_result.append(pion_data[kk])
    
# the coherent cross section
x=mt
y=coherent
y=np.log(y+1e-20)
f=interpolate.interp1d(x,y,kind="cubic")
TT=t_data_coherent
pion_data=f(TT)
pion_data=np.exp(pion_data)-1e-20
for kk in range(len(TT)):
    model_result.append(pion_data[kk])
model_result=np.array(model_result)
# output the model results and correspondence parameter file for Bayesian analysis 
np.savetxt("output.txt",model_result)
phi66 = open('parameters.txt', 'a')
f=open("input")
lines=f.readlines()
# only the upper 5 parameters are changed.
for kk in range(5):
    phi66.write(lines[kk])
phi66.close()




