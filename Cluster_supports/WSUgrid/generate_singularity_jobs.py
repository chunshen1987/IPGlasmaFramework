#!/usr/bin/env python3
"""This script generate all the running jobs.""" 
import sys
from os import path, mkdir
import shutil
import subprocess
import argparse
from math import ceil
from glob import glob
import random

known_initial_types = [
    "IPGlasma", "IPsat",
]

support_cluster_list = ["wsugrid", "OSG", "local",]


def write_script_header(cluster, script, n_threads, event_id, walltime,
                        working_folder):
    """This function write the header of the job submission script"""
    mem = 4*n_threads
    if cluster == "wsugrid":
        script.write("""#!/usr/bin/env bash
#SBATCH --job-name event_{0}
#SBATCH -q primary
#SBATCH -N 1
#SBATCH -n {1}
#SBATCH --mem={2:.0f}G
#SBATCH --constraint=intel
#SBATCH -t {3:s}
#SBATCH -e job.err
#SBATCH -o job.log

cd {4:s}
""".format(event_id, n_threads, mem, walltime, working_folder))
    elif cluster in ("local", "OSG"):
        script.write("#!/bin/bash")
    else:
        print("\U0001F6AB  unrecoginzed cluster name :", cluster)
        print("Available options: ", support_cluster_list)
        exit(1)


def write_job_running_script(eventFolder, bayesFlag):
    scriptName = "run_singularity.sh"
    script = open(path.join(eventFolder, scriptName), "w")
    script.write("""#!/usr/bin/env bash

parafile=$1
processId=$2
nev=$3
nth=$4
seed=$5

# Run the singularity container
export PYTHONIOENCODING=utf-8
export PATH="${PATH}:/usr/lib64/openmpi/bin:/usr/local/gsl/2.5/x86_64/bin"
export LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:/usr/local/lib:/usr/local/gsl/2.5/x86_64/lib64"

printf "Start time: `/bin/date`\\n"
printf "Job is running on node: `/bin/hostname`\\n"
printf "system kernel: `uname -r`\\n"
printf "Job running as user: `/usr/bin/id`\\n"

""")
    if bayesFlag:
        script.write("""bayesFile=$6

/home/IPGlasmaFramework/generate_jobs.py -w playground -c OSG -par ${parafile} -id ${processId} -n_th ${nth} -n_ev ${nev} -seed ${seed} -b ${bayesFile}
""")
    else:
        script.write("""
/home/IPGlasmaFramework/generate_jobs.py -w playground -c OSG -par ${parafile} -id ${processId} -n_th ${nth} -n_ev ${nev} -seed ${seed}
""")

    script.write("""(
    cd playground/event_0
    bash submit_job.pbs
)""")
    script.close()
    return scriptName


def generate_event_folders(workingFolder, clusterName, eventId,
                           singularityRepoPath, parameterFile,
                           bayesFlag, bayesFile,
                           eventId0, nEvents, nThreads, wallTime):
    """This function creates the event folder structure"""
    eventFolder = path.join(workingFolder, 'event_{}'.format(eventId))
    mkdir(eventFolder)

    randomSeed = random.SystemRandom().randint(0, 10000000)
    # generate job running script
    executeScriptName = write_job_running_script(eventFolder, bayesFlag)
    parameterFileName = parameterFile.split('/')[-1]
    script = open(path.join(eventFolder, "submit_job.pbs"), "w")
    write_script_header(clusterName, script, nThreads, eventId, wallTime,
                        eventFolder)
    if bayesFlag:
        script.write("""
singularity exec {0} bash {1} {2} {3} {4} {5} {6} {7}

mkdir -p temp
./collect_events.sh playground temp
mv temp/playground/playground.h5 RESULTS_{8}.h5
""".format(singularityRepoPath, executeScriptName, parameterFileName,
           eventId0, nEvents, nThreads, randomSeed, bayesFile, eventId))
    else:
        script.write("""
singularity exec {0} ./{1} {2} {3} {4} {5} {6}

mv playground/event_0/RESULTS_{7}.h5 ./
""".format(singularityRepoPath, executeScriptName, parameterFileName,
           eventId0, nEvents, nThreads, randomSeed, eventId))
    script.close()

    # copy files
    shutil.copy(parameterFile, eventFolder)
    if bayesFlag:
        shutil.copy(bayesFile, eventFolder)


def create_a_working_folder(workfolder_path):
    try:
        mkdir(workfolder_path)
    except FileExistsError:
        print("The folder {} exists, do you want to delete it?".format(
            workfolder_path))
        user_answer = input()
        if 'y' in user_answer:
            shutil.rmtree(workfolder_path)
            mkdir(workfolder_path)
        else:
            print("bye~\n")
            exit(0)


def main():
    """This is the main funciton"""
    parser = argparse.ArgumentParser(
        description='\U0000269B Welcome to iEBE-MUSIC package',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-w',
                        '--working_folder_name',
                        metavar='',
                        type=str,
                        default='playground',
                        help='working folder path')
    parser.add_argument('-c',
                        '--cluster_name',
                        metavar='',
                        type=str,
                        choices=support_cluster_list,
                        default='local',
                        help='name of the cluster')
    parser.add_argument('-n',
                        '--n_jobs',
                        metavar='',
                        type=int,
                        default=1,
                        help='number of jobs')
    parser.add_argument('-n_ev',
                        '--n_ev_per_job',
                        metavar='',
                        type=int,
                        default=1,
                        help='number of hydro events per job to run')
    parser.add_argument('-n_th',
                        '--n_threads',
                        metavar='',
                        type=int,
                        default=1,
                        help='number of threads used for each job')
    parser.add_argument('-par',
                        '--par_dict',
                        metavar='',
                        type=str,
                        default='parameters_dict_user_IPGlasma.py',
                        help='user-defined parameter dictionary file')
    parser.add_argument('-singularity',
                        '--singularity',
                        metavar='',
                        type=str,
                        default='ipglasmaframework_latest.sif',
                        help='path of the singularity image')
    parser.add_argument('-b',
                        '--bayes_file',
                        metavar='',
                        type=str,
                        default='',
                        help='parameters from bayesian analysis')
    parser.add_argument('-seed',
                        '--random_seed',
                        metavar='',
                        type=int,
                        default='-1',
                        help='Random Seed (-1: according to system time)')
    args = parser.parse_args()

    # print out all the arguments
    print("="*40)
    print("\U0000269B   Input parameters")
    print("="*40)
    for iarg in vars(args):
        print("\U0000269B   {}: {}".format(iarg, getattr(args, iarg)))
    print("="*40)

    try:
        working_folder_name = args.working_folder_name
        cluster_name = args.cluster_name
        n_jobs = args.n_jobs
        n_ev_per_job = args.n_ev_per_job
        n_threads = args.n_threads
        seed = args.random_seed
        singularityRepoPath = path.abspath(args.singularity)
        parameterFile = args.par_dict
        bayesFile = args.bayes_file
        if bayesFile == "":
            bayesFlag = False
        else:
            bayesFlag = True
    except:
        parser.print_help()
        exit(0)

    code_package_path = path.abspath(path.dirname(__file__))
    par_diretory = path.dirname(path.abspath(args.par_dict))
    sys.path.insert(0, par_diretory)
    parameter_dict = __import__(args.par_dict.split('.py')[0].split("/")[-1])
    wallTime = parameter_dict.control_dict['walltime']

    working_folder_name = path.abspath(working_folder_name)
    create_a_working_folder(working_folder_name)

    shutil.copy(args.par_dict, working_folder_name)
    if bayesFlag:
        shutil.copy(bayesFile, working_folder_name)

    toolbar_width = 40
    sys.stdout.write("\U0001F375  Generating {} jobs [{}]".format(
        n_jobs, " "*toolbar_width))
    sys.stdout.flush()
    sys.stdout.write("\b"*(toolbar_width + 1))
    for i_job in range(n_jobs):
        progress_i = (int(float(i_job + 1)/n_jobs*toolbar_width)
                      - int(float(i_job)/n_jobs*toolbar_width))
        for ii in range(progress_i):
            sys.stdout.write("#")
            sys.stdout.flush()
        generate_event_folders(working_folder_name, cluster_name, i_job,
                               singularityRepoPath, parameterFile,
                               bayesFlag, bayesFile, i_job*n_ev_per_job,
                               n_ev_per_job, n_threads, wallTime)
    sys.stdout.write("\n")
    sys.stdout.flush()

    # copy script to collect final results
    pwd = path.abspath(".")
    script_path = path.join(code_package_path, "Cluster_supports/WSUgrid")
    shutil.copy(path.join(script_path, 'collect_singularity_events.sh'), pwd)
    script_path = path.join(code_package_path, "utilities")
    shutil.copy(path.join(script_path, 'combine_multiple_hdf5.py'), pwd)

    if cluster_name == "wsugrid":
        shutil.copy(
            path.join(code_package_path,
                      'Cluster_supports/WSUgrid/submit_all_jobs.sh'), pwd)


if __name__ == "__main__":
    main()
