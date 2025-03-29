#!/usr/bin/env python3

import numpy as np
from sys import argv, exit
from os import path, mkdir
import h5py
from scipy import interpolate
from scipy.integrate import simpson
import shutil
#xp = (M^2+Q^2-t)/(W^2+Q^2-m_N^2)
HBARC = 0.197327053
MJpsi = 3.097 
mN = 0.938
Q2 = 0.0
x_i = 0.0017052045820237158
print(  (x_i * mN**2 + MJpsi**2 ) /x_i, 75**2)
    
    
#if len(argv) != 2:
#    print("Usage: compute_totalCrossSections.py <input_file>")
#    exit(1)

# analysis begins ...

hf = h5py.File(argv[1], "r")
event_list = list(hf.keys())
ampList = list(hf.get(event_list[0]).keys())
xList = list(set([x.split("_")[-1] for x in ampList]))

crossSections = []
crossSectionsErr = []
for x_i in xList:
    realpart = []
    imagpart = []
    b_arr = np.array([])
    for iev, event_name in enumerate(event_list):
        #event_id = int(event_name.split("_")[-1])
        event_id = (event_name.split("_")[-1])
        #event_id = int(0)
        #numbers = re.findall(r'\d+', event_id)
        #event_id = [int(number) for number in numbers]
        #event_id = event_id[0]
        event_group = hf.get(event_name)
        for ifile, fileName in enumerate(event_group.keys()):
            if x_i in fileName:
                temp_data1 = np.nan_to_num(event_group.get(fileName))
                if temp_data1.shape == (0,): continue

                realpart.append(temp_data1[:, 1])
                imagpart.append(temp_data1[:, 2])
                if len(b_arr) == 0:
                    b_arr = temp_data1[:, 0]

    b_arr = np.array(b_arr)
    realpart = np.array(realpart)
    imagpart = np.array(imagpart)
    nev = len(realpart[:, 0])

    prefactor = 1e7*HBARC*HBARC/(8.*np.pi)

    # Compute the integrated cross section
    # Perform Jackknife resampling to determine the error
    # Randomly delete 20% of the events and then compute real_mean, imag_mean
    number_Jackknife = 10000
    delete_d_events = int(nev*0.2)
    real_mean_jackknife = []
    imag_mean_jackknife = []
    for i in range(number_Jackknife):
        idx = np.random.choice(nev, nev - delete_d_events, replace=False)
        real_mean_jackknife.append(np.mean(realpart[idx, :], axis=0))
        imag_mean_jackknife.append(np.mean(imagpart[idx, :], axis=0))
    real_mean_jackknife = np.array(real_mean_jackknife)
    imag_mean_jackknife = np.array(imag_mean_jackknife)

    integrated_cross_section = []
    for i in range(number_Jackknife):
        coherent_jackknife = (real_mean_jackknife[i, :]**2. 
                              + imag_mean_jackknife[i, :]**2.)*prefactor
        #integral_coherent = np.sum(coherent_jackknife * b_arr) * (b_arr[1] - b_arr[0])
        integral_coherent = simpson(coherent_jackknife*b_arr, x=b_arr)
        integrated_cross_section.append(integral_coherent)
    integrated_cross_section = np.array(integrated_cross_section)

    # compute the mean and standard deviation of the integrated cross section
    mean_integrated_cross_section = np.mean(integrated_cross_section)
    variance_samples = np.var(integrated_cross_section)
    integrated_cross_section_err = np.sqrt(
        (nev - delete_d_events) / nev * variance_samples)

    crossSections.append(mean_integrated_cross_section)
    crossSectionsErr.append(integrated_cross_section_err)
hf.close()

xList = np.array([float(x_i) for x_i in xList])
sorted_indices = np.argsort(-xList)
ALL = []
#xp = (M^2+Q^2-t)/(W^2+Q^2-m_N^2)
MJpsi = 3.097 
mN = 0.938
Q2 = 0.0
for idx in sorted_indices:
    x_i = xList[idx]
    rel_err = crossSectionsErr[idx]/crossSections[idx]
    mid = []
    W2 = (x_i * mN**2 + MJpsi**2 ) /x_i
    W = W2**0.5
    mid.append(W)
    mid.append(crossSections[idx])
    mid.append(crossSectionsErr[idx])
    ALL.append(mid)
    print(f"x = {x_i:.3e}: sigma = {crossSections[idx]:.3e} +/- {crossSectionsErr[idx]:.3e} nb, rel_err = {rel_err:.3e}")
ALL = np.array(ALL)
np.savetxt("pp_integrated_Diffraction.txt",
        ALL, fmt="%.6e", delimiter="  ",
        header="W   coh_cs.  coh_cs_err")
