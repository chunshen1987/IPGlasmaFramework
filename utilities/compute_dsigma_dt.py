#!/usr/bin/env python3

import numpy as np
from sys import argv, exit
from os import path, mkdir
import h5py
from scipy import interpolate
import shutil


HBARC = 0.197327053


# the incoherent H1 data  (<W>=75 GeV)
t_data_incoherent = np.array([0.1, 0.29, 0.52, 0.78, 1.12, 1.55, 2.21, 3.3, 5.71])
dsigmadt_data_incoherent = np.array(
        [47.3, 43.8, 36.7, 27.8, 16.8, 10.05, 6.04, 2.8, 0.875])
dsigmadt_data_incoherent_error = np.array(
        [6.7, 6.0, 5.1, 4.2, 2.59, 1.56, 0.68, 0.38, 0.178])

# input the coherent H1 data  (<W>=75 GeV)
t_data_coherent = np.array([0.02, 0.08, 0.14, 0.21, 0.3, 0.41, 0.58, 0.9])
dsigmadt_data_coherent = np.array(
        [336.0, 240.5, 161.2, 111.4, 70.4, 41.2, 18.0, 4.83])
dsigmadt_data_coherent_error = np.array(
        [18.4, 12.9, 9.3, 7.0, 5.1, 3.7, 2.74, 1.75])


try:
    data_path = path.abspath(argv[1])
    data_name = data_path.split("/")[-1]
    results_folder_name = data_name.split(".h5")[0]
    avg_folder_header = path.join(results_folder_name)
    print("output folder: %s" % avg_folder_header)
    if(path.isdir(avg_folder_header)):
        print("folder %s already exists!" % avg_folder_header)
        var = input("do you want to delete it? [y/N]")
        if 'y' in var:
            shutil.rmtree(avg_folder_header)
        else:
            print("please choose another folder path~")
            exit(0)
    mkdir(avg_folder_header)
except IndexError:
    print("Usage: {} results.h5 results_folder".format(argv[0]))
    exit(1)


# analysis begins ...

hf = h5py.File(data_path, "r")
event_list = list(hf.keys())
ampList = list(hf.get(event_list[0]).keys())
xList = list(set([x.split("_")[-1] for x in ampList]))

for x_i in xList:
    try:
        float(x_i)
    except (ValueError,TypeError):
        print("Skip x_i=",x_i)
        continue
    
    realpart = []
    imagpart = []
    t_arr = np.array([])
    for iev, event_name in enumerate(event_list):
        event_id = int(event_name.split("_")[-1])
        event_group = hf.get(event_name)
        for ifile, fileName in enumerate(event_group.keys()):
            # Only include the differential cross sectoin data
            if not fileName.startswith("Amp_"): 
                continue
            if x_i in fileName:
                temp_data1 = np.nan_to_num(event_group.get(fileName))
                if temp_data1.shape == (0,): continue

                realpart.append(temp_data1[:, 1])
                imagpart.append(temp_data1[:, 2])
                if len(t_arr) == 0:
                    t_arr = temp_data1[:, 0]

    t_arr = np.array(t_arr)
    realpart = np.array(realpart)
    imagpart = np.array(imagpart)
    nev = len(realpart[:, 0])
    print("total number of events: {}".format(nev))

    real_mean = np.mean(realpart, axis=0)
    imag_mean = np.mean(imagpart, axis=0)
    real_std = np.std(realpart, axis=0)
    imag_std = np.std(imagpart, axis=0)
    real_sq_mean = np.mean(realpart**2., axis=0)
    imag_sq_mean = np.mean(imagpart**2., axis=0)
    real_sq_std = np.std(realpart**2., axis=0)
    imag_sq_std = np.std(imagpart**2., axis=0)

    prefactor = 1e7*HBARC*HBARC*1.43/(16*np.pi)

    coherent = (real_mean**2. + imag_mean**2.)*prefactor
    coherent_err = 2.*(np.abs(real_mean)*real_std
                       + np.abs(imag_mean)*imag_std)*prefactor/np.sqrt(nev)

    incoherent = (real_sq_mean + imag_sq_mean
                  - real_mean**2 - imag_mean**2.)*prefactor
    incoherent_err = (
        (real_sq_std + imag_sq_std
         + 2.*(np.abs(real_mean)*real_std + np.abs(imag_mean)*imag_std)
        )*prefactor/np.sqrt(nev)
    )
    output = np.array([t_arr, coherent, coherent_err,
                       incoherent, incoherent_err])
    np.savetxt(path.join(avg_folder_header, f"Diffraction_x_{x_i}.txt"),
               output.transpose(), fmt="%.6e", delimiter="  ",
               header="t  coh.  coh_err  incoh.  incoh_err")

    # interpolate the coherent/incoherent cross section to the exp. data points
    f_coh = interpolate.interp1d(t_arr, np.log(coherent + 1e-30), kind="cubic")
    f_coh_err = interpolate.interp1d(t_arr, np.log(coherent_err + 1e-30),
                                     kind="cubic")
    f_incoh = interpolate.interp1d(t_arr, np.log(incoherent + 1e-30),
                                   kind="cubic")
    f_incoh_err = interpolate.interp1d(t_arr, np.log(incoherent_err + 1e-30),
                                       kind="cubic")
    TT = t_data_coherent
    coh_data = np.exp(f_coh(TT))
    coh_data_err = np.exp(f_coh_err(TT))

    TT = t_data_incoherent[0:7]  # only consider 0-2.5 GeV 
    incoh_data = np.exp(f_incoh(TT))
    incoh_data_err = np.exp(f_incoh_err(TT))

    t_arr = np.concatenate((t_data_incoherent[0:7], t_data_coherent))
    model_result = np.concatenate((incoh_data, coh_data))
    model_err = np.concatenate((incoh_data_err, coh_data_err))
    np.savetxt(path.join(avg_folder_header, f"Bayesian_output_x_{x_i}.txt"),
               np.array([t_arr, model_result, model_err]).transpose(),
               fmt="%.6e", delimiter="  ",
               header="t  results  stat. err")
hf.close()
