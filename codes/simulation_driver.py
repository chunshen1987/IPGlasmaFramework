#!/usr/bin/env python3
"""This is a drive script to run hydro + hadronic cascade simulation"""

from multiprocessing import Pool
from subprocess import call
from os import path, mkdir, remove, makedirs
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
          + "save_ipglasma_flag seed_add")


def get_initial_condition(initial_type, iev, seed_add, final_results_folder):
    """This funciton get initial conditions"""
    if "IPGlasma" in initial_type:
        ipglasma_local_folder = "ipglasma/ipglasma_results"
        file_name = ("epsilon-u-Hydro-t0.4-{}.dat".format(iev))
        # check existing events ...
        ipglasma_folder_name = "ipglasma_results_{}".format(iev)
        res_path = path.join(path.abspath(final_results_folder),
                             ipglasma_folder_name)

        if not path.exists(path.join(res_path, file_name)):
            run_ipglasma(iev)
            collect_ipglasma_event(final_results_folder, iev)
        else:
            print("IPGlasma event exists ...")
            print("No need to rerun ...")

        connect_ipglasma_event(final_results_folder, initial_type,
                               iev, file_name)
        return file_name
    else:
        print("\U0001F6AB  "
              + "Do not recognize the initial condition type: {}".format(
                  initial_type))
        exit(1)


def run_ipglasma(iev):
    """This functions run IPGlasma"""
    print("\U0001F3B6  Run IPGlasma ... ")
    call("bash ./run_ipglasma.sh {}".format(iev), shell=True)


def collect_ipglasma_event(final_results_folder, event_id):
    """This function collects the ipglasma results"""
    ipglasma_folder_name = "ipglasma_results_{}".format(event_id)
    res_path = path.join(path.abspath(final_results_folder),
                         ipglasma_folder_name)
    if path.exists(res_path):
        shutil.rmtree(res_path)
    shutil.move("ipglasma/ipglasma_results", res_path)


def connect_ipglasma_event(final_results_folder, initial_type, event_id,
                           filename):
    ipglasma_folder_name = "ipglasma_results_{}".format(event_id)
    res_path = path.join(path.abspath(final_results_folder),
                         ipglasma_folder_name)
    if initial_type == "IPGlasma":
        hydro_initial_file = "MUSIC/initial/epsilon-u-Hydro.dat"
        if path.islink(hydro_initial_file):
            remove(hydro_initial_file)
        call("ln -s {0:s} {1:s}".format(path.join(res_path, filename),
                                        hydro_initial_file),
             shell=True)
    elif initial_type == "IPGlasma+KoMPoST":
        kompost_initial_file = "kompost/Tmunu.dat"
        if path.islink(kompost_initial_file):
            remove(kompost_initial_file)
        call("ln -s {0:s} {1:s}".format(path.join(res_path, filename),
                                        kompost_initial_file),
             shell=True)


def check_an_event_is_good(event_folder):
    """This function checks the given event contains all required files"""
    required_files_list = [
        'particle_9999_vndata_eta_-0.5_0.5.dat',
        'particle_9999_vndata_diff_eta_0.5_2.dat',
        'particle_9999_vndata_eta_-2_2.dat',
        'particle_211_vndata_diff_y_-0.5_0.5.dat',
        'particle_321_vndata_diff_y_-0.5_0.5.dat',
        'particle_2212_vndata_diff_y_-0.5_0.5.dat',
        'particle_-211_vndata_diff_y_-0.5_0.5.dat',
        'particle_-321_vndata_diff_y_-0.5_0.5.dat',
        'particle_-2212_vndata_diff_y_-0.5_0.5.dat',
        'particle_3122_vndata_diff_y_-0.5_0.5.dat',
        'particle_3312_vndata_diff_y_-0.5_0.5.dat',
        'particle_3334_vndata_diff_y_-0.5_0.5.dat',
        'particle_-3122_vndata_diff_y_-0.5_0.5.dat',
        'particle_-3312_vndata_diff_y_-0.5_0.5.dat',
        'particle_-3334_vndata_diff_y_-0.5_0.5.dat',
        'particle_333_vndata_diff_y_-0.5_0.5.dat',
    ]
    event_file_list = glob(path.join(event_folder, "*"))
    for ifile in required_files_list:
        filename = path.join(event_folder, ifile)
        if filename not in event_file_list:
            print("event {} is bad, missing {} ...".format(
                event_folder, filename),
                  flush=True)
            return False
    return True


def zip_results_into_hdf5(final_results_folder, event_id, para_dict):
    """This function combines all the results into hdf5"""
    results_name = "spvn_results_{}".format(event_id)
    time_stamp = para_dict['time_stamp_str']
    initial_state_filelist = [
        'epsilon-u-Hydro-t0.1-{}.dat'.format(event_id),
        'epsilon-u-Hydro-t{0}-{1}.dat'.format(time_stamp, event_id),
        'NcollList{}.dat'.format(event_id), 'NpartList{}.dat'.format(event_id),
        'NpartdNdy-t0.6-{}.dat'.format(event_id),
        'NgluonEstimators{}.dat'.format(event_id)
    ]
    pre_equilibrium_filelist = [
        'ekt_tIn01_tOut08.music_init_flowNonLinear_pimunuTransverse.txt'
    ]
    hydro_info_filepattern = [
        "eccentricities_evo_eta_*.dat", "momentum_anisotropy_eta_*.dat",
        "inverse_Reynolds_number_eta_*.dat",
        "averaged_phase_diagram_trajectory_eta_*.dat",
        "global_conservation_laws.dat", "global_angular_momentum_*.dat",
        "vorticity_*.dat", "strings_*.dat"
    ]

    hydrofolder = path.join(final_results_folder,
                            "hydro_results_{}".format(event_id))
    spvnfolder = path.join(final_results_folder, results_name)

    status = check_an_event_is_good(spvnfolder)
    if status:
        curr_time = time.asctime()
        print("[{}] {} is good, converting results to hdf5".format(
            curr_time, spvnfolder),
              flush=True)

        if para_dict['initial_condition'] == "self":
            # save initial conditions
            if ("IPGlasma" in para_dict['initial_type']
                    and para_dict['save_ipglasma']):
                initial_folder = path.join(
                    final_results_folder,
                    "ipglasma_results_{}".format(event_id))
                for inifilename in initial_state_filelist:
                    inifile = path.join(initial_folder, inifilename)
                    if path.isfile(inifile):
                        shutil.move(inifile, spvnfolder)

            # save pre-equilibrium results
            if (para_dict['initial_type'] == "IPGlasma+KoMPoST"
                    and para_dict['save_kompost']):
                preeq_folder = path.join(final_results_folder,
                                         "kompost_results_{}".format(event_id))
                for prefilename in pre_equilibrium_filelist:
                    prefile = path.join(preeq_folder, prefilename)
                    if path.isfile(prefile):
                        shutil.move(prefile, spvnfolder)

        # save hydro evolution information
        for ipattern in hydro_info_filepattern:
            hydro_info_list = glob(path.join(hydrofolder, ipattern))
            for ihydrofile in hydro_info_list:
                if path.isfile(ihydrofile):
                    shutil.move(ihydrofile, spvnfolder)

        hf = h5py.File("{0}.h5".format(results_name), "w")
        gtemp = hf.create_group("{0}".format(results_name))
        file_list = glob(path.join(spvnfolder, "*"))
        for file_path in file_list:
            file_name = file_path.split("/")[-1]
            dtemp = np.loadtxt(file_path)
            h5data = gtemp.create_dataset("{0}".format(file_name),
                                          data=dtemp,
                                          compression="gzip",
                                          compression_opts=9)
            # save header
            ftemp = open(file_path, "r")
            header_text = str(ftemp.readline())
            ftemp.close()
            if header_text.startswith("#"):
                h5data.attrs.create("header", np.string_(header_text))
        hf.close()
        shutil.move("{}.h5".format(results_name), final_results_folder)
        shutil.rmtree(spvnfolder, ignore_errors=True)
    else:
        print("{} is broken, skipped".format(spvnfolder), flush=True)
    return (status)


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


def main(para_dict_):
    """This is the main function"""
    initial_type = para_dict_['initial_type']
    num_threads = para_dict_['num_threads']
    curr_time = time.asctime()
    print("\U0001F3CE  [{}] Number of threads: {}".format(curr_time,
                                                          num_threads),
          flush=True)

    idx0 = para_dict_['event_id0']
    nev = 1
    for iev in range(idx0, idx0 + nev):
        curr_time = time.asctime()

        event_id = str(iev)
        final_results_folder = "EVENT_RESULTS_{}".format(event_id)
        if path.exists(final_results_folder):
            print("{} exists ...".format(final_results_folder), flush=True)
            results_file = path.join(final_results_folder,
                                     "results_{}.h5".format(event_id))
            status = False
            if path.exists(results_file):
                status = True
                spvnfolder = path.join(final_results_folder,
                                       "results_{}".format(event_id))
                if path.exists(spvnfolder):
                    status = check_an_event_is_good(spvnfolder)
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

        ifile = get_initial_condition(initial_type,
                                      iev,
                                      para_dict_['seed_add'],
                                      final_results_folder)

        # zip results into a hdf5 database
        status = zip_results_into_hdf5(final_results_folder, event_id,
                                       para_dict_)

        # remove the unwanted outputs if event is finished properly
        if status:
            remove_unwanted_outputs(final_results_folder, event_id,
                                    para_dict_['save_ipglasma'])


if __name__ == "__main__":
    try:
        INITIAL_CONDITION_TYPE = str(sys.argv[1])
        EVENT_ID0 = int(sys.argv[2])
        N_THREADS = int(sys.argv[3])
        SAVE_IPGLASMA = (sys.argv[4].lower() == "true")
        SEED_ADD = int(sys.argv[5])
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
        'num_threads': N_THREADS,
        'save_ipglasma': SAVE_IPGLASMA,
        'seed_add': SEED_ADD,
    }

    main(para_dict)
