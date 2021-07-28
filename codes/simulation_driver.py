#!/usr/bin/env python3
"""This is a drive script to run hydro + hadronic cascade simulation"""

from multiprocessing import Pool
from subprocess import call
from os import path, mkdir, remove, makedirs, system
from glob import glob
import sys
import time
import shutil
import re
import h5py
import numpy as np


def print_usage():
    """This function prints out help messages"""
    print("\U0001F3B6  " + "Usage: {} ".format(sys.argv[0])
          + "initial_condition_type event_id n_threads"
          + "save_ipglasma_flag")


def get_initial_condition(initial_type, iev, final_results_folder):
    """This funciton get initial conditions"""
    if "IPGlasma" in initial_type:
        run_ipglasma(iev)
        res_path = collect_ipglasma_event(final_results_folder, iev)
        WilsonLineFileList = glob(path.join(res_path, "V-*"))
        return(WilsonLineFileList)
    else:
        print("\U0001F6AB  "
              + "Do not recognize the initial condition type: {}".format(
                  initial_type))
        exit(1)


def run_ipglasma(iev):
    """This functions run IPGlasma"""
    print("\U0001F3B6  Run IPGlasma ... ")
    call("bash ./run_ipglasma.sh {}".format(iev), shell=True)


def run_subnucleondiffraction(WilsonLineFileList, iev, final_results_folder):
    """This functions run subnucleon diffraction"""
    print("\U0001F3B6  Run subnucleondiffraction ... ")
    for ifile, filename in enumerate(WilsonLineFileList):
        call("bash ./run_subnucleondiffraction.sh {} {} {}".format(iev, ifile,
                                                                   filename),
             shell=True)
    res_folder_name = "subnucleondiffraction_results_{}".format(iev)
    res_path = path.join(path.abspath(final_results_folder),
                         res_folder_name)
    if path.exists(res_path):
        shutil.rmtree(res_path)
    shutil.move("subnucleondiffraction/subnucleondiffraction_results",
                res_path)


def collect_ipglasma_event(final_results_folder, event_id):
    """This function collects the ipglasma results"""
    ipglasma_folder_name = "ipglasma_results_{}".format(event_id)
    res_path = path.join(path.abspath(final_results_folder),
                         ipglasma_folder_name)
    if path.exists(res_path):
        shutil.rmtree(res_path)
    shutil.move("ipglasma/ipglasma_results", res_path)
    return(res_path)


def zip_results_into_hdf5(final_results_folder, event_id, para_dict):
    """This function combines all the results into hdf5"""
    results_name = "event_{}".format(event_id)
    initial_state_filelist = [
        'NcollList{}.dat'.format(event_id),
        'NpartList{}.dat'.format(event_id),
        'NpartdNdy-t0.6-{}.dat'.format(event_id),
        'NgluonEstimators{}.dat'.format(event_id)
    ]

    resfolder = path.join(final_results_folder, results_name)
    if path.exists(resfolder):
        shutil.rmtree(resfolder)
    mkdir(resfolder)

    curr_time = time.asctime()
    print("[{}] converting {} to hdf5".format(curr_time, resfolder),
          flush=True)

    if ("IPGlasma" in para_dict['initial_type']
            and para_dict['save_ipglasma']):
        initial_folder = path.join(
            final_results_folder,
            "ipglasma_results_{}".format(event_id))
        for inifilename in initial_state_filelist:
            inifile = path.join(initial_folder, inifilename)
            if path.isfile(inifile):
                shutil.move(inifile, resfolder)
    diffraction_folder = path.join(
            final_results_folder,
            "subnucleondiffraction_results_{}".format(event_id))
    diffraction_filelist = glob(path.join(diffraction_folder, "*"))
    for file_i in diffraction_filelist:
        shutil.move(file_i, resfolder)

    hf = h5py.File("{0}.h5".format(results_name), "w")
    gtemp = hf.create_group("{0}".format(results_name))
    file_list = glob(path.join(resfolder, "*"))
    for file_path in file_list:
        file_name = file_path.split("/")[-1]
        dtemp = np.loadtxt(file_path)
        h5data = gtemp.create_dataset("{0}".format(file_name),
                                      data=dtemp,
                                      compression="gzip",
                                      compression_opts=9)
    hf.close()
    shutil.move("{}.h5".format(results_name), final_results_folder)
    shutil.rmtree(resfolder, ignore_errors=True)
    return(True)


def remove_unwanted_outputs(final_results_folder,
                            event_id,
                            save_ipglasma=True):
    """
        This function removes all hydro surface file and UrQMD results
        if they are unwanted to save space

    """
    if not save_ipglasma:
        ipglasmafolder = path.join(final_results_folder,
                                   "ipglasma_results_{}".format(event_id))
        shutil.rmtree(ipglasmafolder, ignore_errors=True)


def combine_all_hdf5_results(idx):
    """
        This functions combine all the hdf5 files into one
    """
    RESULTS_NAME = "RESLUTS_{}".format(idx)
    EVENT_LIST = glob("EVENT_RESULTS_*/*.h5")
    exist_group_keys = []
    for ievent, event_path in enumerate(EVENT_LIST):
        print("processing {0} ... ".format(event_path))
        event_name = event_path.split("/")[-1]
        hftemp = h5py.File(event_path, "r")
        glist = list(hftemp.keys())
        hftemp.close()
        for igroup, gtemp in enumerate(glist):
            gtemp2 = gtemp
            random_string_len = 1
            tol = 0
            while gtemp2 in exist_group_keys:
                randomlabel = randomString(random_string_len)
                gtemp2 = "{0}{1}".format(gtemp, randomlabel)
                tol += 1
                if tol > 30:
                    random_string_len += 1
                    tol = 0
            if gtemp2 != gtemp:
                print("Conflict in mergeing {0}, use {1}".format(gtemp, gtemp2))
            exist_group_keys.append(gtemp2)
            system('h5copy -i {0} -o {1}.h5 -s {2} -d {3}'.format(
                event_path, RESULTS_NAME, gtemp, gtemp2))




def main(para_dict_):
    """This is the main function"""
    initial_type = para_dict_['initial_type']
    num_threads = para_dict_['num_threads']
    curr_time = time.asctime()
    print("\U0001F3CE  [{}] Number of threads: {}".format(curr_time,
                                                          num_threads),
          flush=True)

    nev = para_dict_['n_events']
    idx0 = para_dict_['event_id0']*nev
    for iev in range(idx0, idx0 + nev):
        curr_time = time.asctime()

        event_id = str(iev)
        final_results_folder = "EVENT_RESULTS_{}".format(event_id)
        if path.exists(final_results_folder):
            print("{} exists ...".format(final_results_folder), flush=True)
            results_file = path.join(final_results_folder,
                                     "event_{}.h5".format(event_id))
            status = False
            if path.exists(results_file):
                status = True
            if status:
                print(
                    "{} finished properly. No need to rerun.".format(event_id),
                    flush=True)
                continue
            print("Rerun {} ...".format(final_results_folder), flush=True)
        else:
            mkdir(final_results_folder)
        print("[{}] Generate initial condition ... ".format(curr_time),
              flush=True)

        WilsonLineFileList = get_initial_condition(
                            initial_type, iev, final_results_folder)
        run_subnucleondiffraction(
                            WilsonLineFileList, iev, final_results_folder)

        # zip results into a hdf5 database
        status = zip_results_into_hdf5(final_results_folder, event_id,
                                       para_dict_)

        # remove the unwanted outputs if event is finished properly
        if status:
            remove_unwanted_outputs(final_results_folder, event_id,
                                    para_dict_['save_ipglasma'])
    combine_all_hdf5_results(para_dict_['event_id0'])


if __name__ == "__main__":
    try:
        INITIAL_CONDITION_TYPE = str(sys.argv[1])
        EVENT_ID0 = int(sys.argv[2])
        N_EVENTS = int(sys.argv[3])
        N_THREADS = int(sys.argv[4])
        SAVE_IPGLASMA = (sys.argv[5].lower() == "true")
        #SEED = int(sys.argv[6])
    except IndexError:
        print_usage()
        exit(0)

    known_initial_types = [
        "IPGlasma", "IPSat"
    ]

    if INITIAL_CONDITION_TYPE not in known_initial_types:
        print("\U0001F6AB  "
              + "Do not recognize the initial condition type: {}".format(
                  INITIAL_CONDITION_TYPE),
              flush=True)
        exit(1)

    para_dict = {
        'initial_type': INITIAL_CONDITION_TYPE,
        'event_id0': EVENT_ID0,
        'n_events': N_EVENTS,
        'num_threads': N_THREADS,
        'save_ipglasma': SAVE_IPGLASMA,
        #'random_seed': SEED,
    }

    main(para_dict)
