#!/usr/bin/env python3

from numpy import *
from sys import argv, exit
from os import path, mkdir
import h5py
from scipy import interpolate
import shutil


HBARC = 0.197327053


# the incoherent H1 data  (<W>=75 GeV)
t_data_incoherent = array([0.1, 0.29, 0.52, 0.78, 1.12, 1.55, 2.21, 3.3, 5.71])
dsigmadt_data_incoherent = array(
        [47.3, 43.8, 36.7, 27.8, 16.8, 10.05, 6.04, 2.8, 0.875])
dsigmadt_data_incoherent_error = array(
        [6.7, 6.0, 5.1, 4.2, 2.59, 1.56, 0.68, 0.38, 0.178])

# input the coherent H1 data  (<W>=75 GeV)
t_data_coherent = array([0.02, 0.08, 0.14, 0.21, 0.3, 0.41, 0.58, 0.9])
dsigmadt_data_coherent = array(
        [336.0, 240.5, 161.2, 111.4, 70.4, 41.2, 18.0, 4.83])
dsigmadt_data_coherent_error = array(
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
nev = len(event_list)
print("total number of events: {}".format(nev))


realpart = []
imagpart = []
t_arr = []
for iev, event_name in enumerate(event_list):
    event_id = int(event_name.split("_")[-1])
    event_group = hf.get(event_name)
    for ifile in range(2):
        filename = "real_{}_{}".format(event_id, ifile)
        temp_data = event_group.get(filename)
        temp_data = nan_to_num(temp_data)
        if iev == 0 and ifile == 0:
            t_arr = temp_data[:, 0]
        realpart.append(temp_data[:, 1])
        filename = "imag_{}_{}".format(event_id, ifile)
        temp_data = event_group.get(filename)
        temp_data = nan_to_num(temp_data)
        imagpart.append(temp_data[:, 1])
hf.close()

t_arr = array(t_arr)
realpart = array(realpart)
imagpart = array(imagpart)

real_mean = mean(realpart, axis=0)
imag_mean = mean(imagpart, axis=0)
real_std = std(realpart, axis=0)
imag_std = std(imagpart, axis=0)
real_sq_mean = mean(realpart**2., axis=0)
imag_sq_mean = mean(imagpart**2., axis=0)
real_sq_std = std(realpart**2., axis=0)
imag_sq_std = std(imagpart**2., axis=0)

squaremean = (mean(realpart**2., axis=0) + mean(imagpart**2., axis=0))/(16*pi)
prefactor = 1e7*HBARC*HBARC*1.43/(16*pi)

coherent = (real_mean**2. + imag_mean**2.)*prefactor
coherent_err = 2.*(abs(real_mean)*real_std
                   + abs(imag_mean)*imag_std)*prefactor/sqrt(nev)

incoherent = (real_sq_mean + imag_sq_mean
              - real_mean**2 - imag_mean**2.)*prefactor
incoherent_err = (real_sq_std + imag_sq_std
                  - 2.*(abs(real_mean)*real_std + abs(imag_mean)*imag_std)
                 )*prefactor/sqrt(nev)

# interpolate the coherent/incoherent cross section to the exp. data points
f_coh = interpolate.interp1d(t_arr, log(coherent + 1e-30), kind="cubic")
f_coh_err = interpolate.interp1d(t_arr, log(coherent_err + 1e-30),
                                 kind="cubic")
f_incoh = interpolate.interp1d(t_arr, log(incoherent + 1e-30), kind="cubic")
f_incoh_err = interpolate.interp1d(t_arr, log(incoherent_err + 1e-30),
                                   kind="cubic")
TT = t_data_coherent
coh_data = exp(f_coh(TT))
coh_data_err = exp(f_coh_err(TT))

TT = t_data_incoherent[0:7]  # only consider 0-2.5 GeV 
incoh_data = exp(f_incoh(TT))
incoh_data_err = exp(f_incoh_err(TT))

model_result = concatenate((incoh_data, coh_data))
model_err = concatenate((incoh_data_err, coh_data_err))
savetxt(path.join(avg_folder_header, "output.txt"),
        array([model_result, model_err]).transpose(),
        fmt="%.6e", delimiter="  ",
        header="results  stat. err")
