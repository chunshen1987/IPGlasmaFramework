#!/usr/bin/env python3
"""This script generates the job submission script on OSG"""


import sys
from os import path, makedirs
import random

FILENAME = "singularity.submit"

def print_usage():
    """This function prints out help messages"""
    print("Usage: {} ".format(sys.argv[0].split("/")[-1])
          + "Njobs Nevents_per_job SingularityImage ParameterFile jobId "
          + "[bayesFile]")


def write_submission_script(para_dict_):
    jobName = "IPG_Diffraction_{}".format(para_dict_["job_id"])
    random_seed = random.SystemRandom().randint(0, 10000000)
    imagePathHeader = "osdf://"
    script = open(FILENAME, "w")
    if para_dict_["bayesFlag"]:
        script.write("""universe = vanilla
executable = run_singularity.sh
arguments = {0} $(Process) {1} {2} {3}
""".format(para_dict_["paraFile"], para_dict_["n_events_per_job"],
           random_seed, para_dict_["bayesFile"]))
    else:
        script.write("""universe = vanilla
executable = run_singularity.sh
arguments = {0} $(Process) {1} {2}
""".format(para_dict_["paraFile"], para_dict_["n_events_per_job"],
           random_seed))
    script.write("""
JobBatchName = {0}

should_transfer_files = YES
WhenToTransferOutput = ON_EXIT

+SingularityImage = "{1}"
Requirements = SINGULARITY_CAN_USE_SIF && StringListIMember("stash", HasFileTransferPluginMethods)
""".format(jobName, imagePathHeader + para_dict_["image_with_path"]))

    if para_dict_['bayesFlag']:
        script.write("""
transfer_input_files = {0}, {1}
""".format(para_dict_['paraFile'], para_dict_['bayesFile']))
    else:
        script.write("""
transfer_input_files = {0}
""".format(para_dict_['paraFile']))

    script.write("""
transfer_output_files = playground/event_0/RESULTS_$(Process).h5

error = log/job.$(Cluster).$(Process).error
output = log/job.$(Cluster).$(Process).output
log = log/job.$(Cluster).$(Process).log

#+JobDurationCategory = "Long"
max_idle = 1000

# auto release hold jobs if they are caused by data transfer issues on OSG
periodic_release = ((HoldReasonCode == 13 || HoldReasonCode == 26) && (time() - EnteredCurrentStatus) > 1200 )

# Send the job to Held state on failure.
on_exit_hold = (ExitBySignal == True) || (ExitCode != 0)

# The below are good base requirements for first testing jobs on OSG,
# if you don't have a good idea of memory and disk usage.
request_cpus = 1
request_memory = 2 GB
request_disk = 2 GB

# Queue one job with the above specifications.
queue {0}""".format(para_dict_["n_jobs"]))
    script.close()


def write_job_running_script(para_dict_):
    script = open("run_singularity.sh", "w")
    script.write("""#!/usr/bin/env bash

parafile=$1
processId=$2
nev=$3
seed=$4

# Run the singularity container
export PYTHONIOENCODING=utf-8
export PATH="${PATH}:/usr/lib64/openmpi/bin:/usr/local/gsl/2.5/x86_64/bin"
export LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:/usr/local/lib:/usr/local/gsl/2.5/x86_64/lib64"

printf "Start time: `/bin/date`\\n"
printf "Job is running on node: `/bin/hostname`\\n"
printf "system kernel: `uname -r`\\n"
printf "Job running as user: `/usr/bin/id`\\n"

""")
    if para_dict_["bayesFlag"]:
        script.write("""bayesFile=$5

/opt/IPGlasmaFramework/generate_jobs.py -w playground -c OSG -par ${parafile} -id ${processId} -n_th 1 -n_ev ${nev} -seed ${seed} -b ${bayesFile}
""")
    else:
        script.write("""
/opt/IPGlasmaFramework/generate_jobs.py -w playground -c OSG -par ${parafile} -id ${processId} -n_th 1 -n_ev ${nev} -seed ${seed}
""")

    script.write("""(
    cd playground/event_0
    bash submit_job.script
    mv RESULTS*.h5 RESULTS_${processId}.h5
)
exit 0
""")
    script.close()


def main(para_dict_):
    write_submission_script(para_dict_)
    write_job_running_script(para_dict_)
    logFolderName = "log"
    if not path.exists(logFolderName):
        makedirs(logFolderName)


if __name__ == "__main__":
    bayesFlag = False
    bayesFile = ""
    try:
        N_JOBS = int(sys.argv[1])
        N_EVENTS_PER_JOBS = int(sys.argv[2])
        SINGULARITY_IMAGE_PATH = sys.argv[3]
        SINGULARITY_IMAGE = SINGULARITY_IMAGE_PATH.split("/")[-1]
        PARAMFILE = sys.argv[4]
        JOBID = sys.argv[5]
        if len(sys.argv) == 7:
            bayesFile = sys.argv[6]
            bayesFlag = True
    except (IndexError, ValueError) as e:
        print_usage()
        exit(0)

    para_dict = {
        'n_jobs': N_JOBS,
        'n_events_per_job': N_EVENTS_PER_JOBS,
        'image_name': SINGULARITY_IMAGE,
        'image_with_path': SINGULARITY_IMAGE_PATH,
        'paraFile': PARAMFILE,
        'job_id': JOBID,
        'bayesFlag': bayesFlag,
        'bayesFile': bayesFile,
    }

    main(para_dict)

