#!/usr/bin/env python3
"""This script combine multiple hdf5 data files to one"""

import sys
from os import path, system, remove
from shutil import rmtree
from glob import glob
import h5py
import string
import random
from numpy import nan_to_num

def randomString(stringLength=1):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


def print_help():
    """This function outpus help messages"""
    print("{0} results_folder".format(sys.argv[0]))

def check_an_event_is_good(h5_event):
    """This function checks the given event contains all required files"""
    event_file_list = list(h5_event.keys())
    if len(event_file_list) > 0:
        return True
    else:
        return False

def check_events_are_good(h5_filename):
    """This function is a shell to check all the events status in a h5 file"""
    h5_file = h5py.File(h5_filename, "a")
    event_list = list(h5_file.keys())
    event_status_all = False
    for event_name in event_list:
        test_event = h5_file.get(event_name)
        event_status = check_an_event_is_good(test_event)
        if event_status:
            event_status_all = True
        else:
            print("checking {} ...".format(h5_filename))
            print("delete event {} ...".format(event_name))
            del h5_file[event_name]
    h5_file.close()
    if event_status_all:
        print("{} is good!".format(h5_filename))
    else:
        print("{} is not good! Ignored~".format(h5_filename))
    return(event_status_all)

if len(sys.argv) < 2:
    print_help()
    exit(1)

RESULTS_FOLDER = str(sys.argv[1])
RESULTS_NAME = RESULTS_FOLDER.split("/")[-1]
if RESULTS_NAME == "":
    RESULTS_NAME = RESULTS_FOLDER.split("/")[-2]
RESULTS_PATH = path.abspath(path.join(".", RESULTS_FOLDER))
EVENT_LIST = glob(path.join(RESULTS_PATH, "*.h5"))

exist_group_keys = []

h5Res = h5py.File("{}.h5".format(RESULTS_NAME), "a")
exist_group_keys += list(h5Res.keys())
for ievent, event_path in enumerate(EVENT_LIST):
    print("processing {0} ... ".format(event_path))
    event_folder = "/".join(event_path.split("/")[0:-1])
    try:
        hftemp = h5py.File(event_path, "r")
        glist = list(hftemp.keys())
        if not check_events_are_good(event_path):
            remove(event_path)
            continue
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
            h5py.h5o.copy(hftemp.id, gtemp.encode('UTF-8'),
                          h5Res.id, gtemp2.encode('UTF-8'))
        hftemp.close()
        remove(event_path)
    except:
        continue
h5Res.close()
