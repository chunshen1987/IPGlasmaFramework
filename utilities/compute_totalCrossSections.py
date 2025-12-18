#!/usr/bin/env python3

import numpy as np
from sys import argv, exit
from os import path
import h5py
from scipy.integrate import simpson
import re
import sys

PRINT_FILE_FLAG = False

HBARC = 0.197327053

if len(argv) != 2:
    print("Usage: compute_totalCrossSections.py <input_file>")
    exit(1)

# analysis begins ...

hf = h5py.File(argv[1], "r")
event_list = list(hf.keys())
if len(event_list) == 0: 
    print("No events found in the file.")
    sys.exit(1)
event_data = hf.get(event_list[0])
if event_data is None:
    print(f"Event {event_list[0]} not found or is inaccessible.")
    sys.exit(1)
ampList = list(event_data.keys())
xList = list(set([x.split("_")[-1] for x in ampList]))
if len(xList) == 0:
    print("No amplitudes found in the file.")
    sys.exit(1)

xList_to_sort = [(x, float(x)) for x in xList]
xList_to_sort.sort(key=lambda x: x[1], reverse=True)
xList = [x[0] for x in xList_to_sort]

crossSections = []
crossSectionsErr = []
incoherentCrossSections = []
incoherentCrossSectionsErr = []
for k, x_i in enumerate(xList):
    try:
        float(x_i)
    except (ValueError,TypeError):
        print("Skip x_i=",x_i)
        continue

    realpart = []
    imagpart = []
    sigma_total_transverse = []
    b_arr = np.array([])
    for iev, event_name in enumerate(event_list):
        name_file = event_name.split("_")[-1]
        event_id = int(''.join(re.findall(r'\d+', name_file)))
        event_group = hf.get(event_name)
        for ifile, fileName in enumerate(event_group.keys()):
            # Only include the total cross section data
            if not fileName.startswith("AmpF_"): 
                continue
            if x_i in fileName:
                temp_data1 = np.nan_to_num(event_group.get(fileName))
                if temp_data1.shape == (0,): continue
                if len(temp_data1.shape) == 1: continue

                realpart.append(temp_data1[:, 1])
                imagpart.append(temp_data1[:, 2])
                if len(b_arr) == 0:
                    b_arr = temp_data1[:, 0]

                for key, value in event_group.get(fileName).attrs.items():
                    text = value.decode() if isinstance(value, (bytes, np.bytes_)) else str(value)

                    if "Total cross section (transverse)" in text:
                        # extract number before ' nb'
                        m = re.search(r'([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s*nb', text)
                        if m:
                            sigma_total_transverse.append(float(m.group(1)))

    if len(realpart) == 0:
        print(f"Skip x={x_i} with no data")
        continue

    b_arr = np.array(b_arr)
    realpart = np.array(realpart)
    imagpart = np.array(imagpart)
    sigma_total_transverse = np.array(sigma_total_transverse)
    nev = len(realpart[:, 0])

    prefactor = 1e7*HBARC*HBARC/(8.*np.pi)

    # Compute the integrated cross section
    # Perform Jackknife resampling to determine the error
    # Randomly delete 20% of the events and then compute real_mean, imag_mean
    number_Jackknife = 10000
    delete_d_events = int(nev*0.2)
    if delete_d_events == 0:
        sys.exit("Not enough events for Jackknife resampling.")

    real_mean_jackknife = []
    imag_mean_jackknife = []
    sigma_total_transverse_jackknife = []

    for i in range(number_Jackknife):
        idx = np.random.choice(nev, nev - delete_d_events, replace=False)
        real_mean_jackknife.append(np.mean(realpart[idx, :], axis=0))
        imag_mean_jackknife.append(np.mean(imagpart[idx, :], axis=0))
        sigma_total_transverse_jackknife.append(np.mean(sigma_total_transverse[idx]))

    real_mean_jackknife = np.array(real_mean_jackknife)
    imag_mean_jackknife = np.array(imag_mean_jackknife)
    sigma_total_transverse_jackknife = np.array(sigma_total_transverse_jackknife)

    integrated_cross_section = []
    for i in range(number_Jackknife):
        coherent_jackknife = (real_mean_jackknife[i, :]**2. 
                              + imag_mean_jackknife[i, :]**2.)*prefactor
        integral_coherent = simpson(coherent_jackknife*b_arr, x=b_arr)
        integrated_cross_section.append(integral_coherent)
    integrated_cross_section = np.array(integrated_cross_section)

    # ---- COHERENT CROSS SECTION FOR EACH JACKKNIFE SAMPLE ----

    integrated_cross_section = []
    for i in range(number_Jackknife):
        coherent_jackknife = (real_mean_jackknife[i, :]**2. 
                              + imag_mean_jackknife[i, :]**2.)*prefactor
        integral_coherent = simpson(coherent_jackknife*b_arr, x=b_arr)
        integrated_cross_section.append(integral_coherent)

    integrated_cross_section = np.array(integrated_cross_section)

    # ---- TOTAL & INCOHERENT CROSS SECTIONS ----

    # Coherent mean & jackknife error
    mean_integrated_cross_section = np.mean(integrated_cross_section)
    var_integrated = np.var(integrated_cross_section)
    integrated_cross_section_err = np.sqrt((nev - delete_d_events) / nev * var_integrated)

    # Total mean & jackknife error
    mean_total_integrated_cross_section = np.mean(sigma_total_transverse_jackknife)
    var_total = np.var(sigma_total_transverse_jackknife)
    total_integrated_cross_section_err = np.sqrt((nev - delete_d_events) / nev * var_total)

    # ---- DIRECT COMPUTATION OF INCOHERENT CROSS SECTION ----
    incoherent_samples = sigma_total_transverse_jackknife - integrated_cross_section

    # Incoherent mean & jackknife error
    mean_incoherent = np.mean(incoherent_samples)
    var_incoherent = np.var(incoherent_samples)
    incoherent_err = np.sqrt((nev - delete_d_events) / nev * var_incoherent)

    crossSections.append(mean_integrated_cross_section)
    crossSectionsErr.append(integrated_cross_section_err)
    incoherentCrossSections.append(mean_incoherent)
    incoherentCrossSectionsErr.append(incoherent_err)
hf.close()

def is_number(x_i):
    try:
        float(x_i)
        return True
    except (ValueError, TypeError):
        return False

xList = [x_i for x_i in xList if is_number(x_i)]
xList = np.array([float(x_i) for x_i in xList])
sorted_indices = np.argsort(-xList)

for idx in sorted_indices:
    try: # in practice this makes sure that idx refers to some actual x value
        x_i = xList[idx]
        rel_err = crossSectionsErr[idx]/crossSections[idx]
        rel_err_incoh = incoherentCrossSectionsErr[idx]/incoherentCrossSections[idx]
        print(f"x = {x_i:.3e}: sigma_coh = {crossSections[idx]:.3e} +/- {crossSectionsErr[idx]:.3e} nb, rel_err = {rel_err:.3e}, sigma_incoh = {incoherentCrossSections[idx]:.3e} +/- {incoherentCrossSectionsErr[idx]:.3e} nb, rel_err_incoh = {rel_err_incoh:.3e}")
    except:
        continue

if PRINT_FILE_FLAG:
    source_dir = path.dirname(path.abspath(argv[1]))
    output_file = path.join(source_dir, "total_cross_sections.dat")
    with open(output_file, "w") as of:
        of.write("# x, sigma_coh [nb], sigma_coh_err [nb], sigma_incoh [nb], sigma_incoh_err [nb]\n")
        for idx in sorted_indices:
            try:
                x_i = xList[idx]
                of.write(f"{x_i:.6e} {crossSections[idx]:.6e} {crossSectionsErr[idx]:.6e} {incoherentCrossSections[idx]:.6e} {incoherentCrossSectionsErr[idx]:.6e}\n")
            except:
                continue