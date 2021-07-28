#!/usr/bin/env python3
"""This script generates the job submission script on OSG"""


import sys
from os import path
import random

FILENAME = "singularity.submit"

def print_usage():
    """This function prints out help messages"""
    print("Usage: {} ".format(sys.argv[0].split("/")[-1])
          + "Njobs  Nevents_per_job SingularityImage ParameterFile jobId")


def write_submission_script(para_dict_):
    jobName = "IPG_Diffraction_{}".format(para_dict_["job_id"])
    random_seed = random.SystemRandom().randint(0, 10000000)
    script = open(FILENAME, "w")
    script.write("""universe = vanilla
executable = run_singularity.sh
arguments = {0} $(Process) {1} {2}
JobBatchName = {3}

should_transfer_files = YES
WhenToTransferOutput = ON_EXIT

+SingularityImage = "./{4}"
Requirements = HAS_SINGULARITY == TRUE && SINGULARITY_MODE == "privileged" && (GLIDEIN_ResourceName != "cinvestav")

transfer_input_files = {0}, ../singularity_repos/{4}
transfer_output_files = playground/event_0/RESULTS_$(Process).h5

error = ../log/job.$(Cluster).$(Process).error
output = ../log/job.$(Cluster).$(Process).output
log = ../log/job.$(Cluster).$(Process).log

# Send the job to Held state on failure. 
on_exit_hold = (ExitBySignal == True) || (ExitCode != 0)

# The below are good base requirements for first testing jobs on OSG, 
# if you don't have a good idea of memory and disk usage.
request_cpus = 1
request_memory = 3 GB
request_disk = 1 GB

# Queue one job with the above specifications.
queue {5}""".format(para_dict_["paraFile"], para_dict_["n_events_per_job"],
                    random_seed, jobName, para_dict_["image"],
                    para_dict_["n_jobs"])
    )



def main(para_dict_):
    write_submission_script(para_dict_)


if __name__ == "__main__":
    try:
        N_JOBS = int(sys.argv[1])
        N_EVENTS_PER_JOBS = int(sys.argv[2])
        SINGULARITY_IMAGE = sys.argv[3].split("/")[-1]
        PARAMFILE = sys.argv[4]
        JOBID = int(sys.argv[5])
    except IndexError:
        print_usage()
        exit(0)

    para_dict = {
        'n_jobs': N_JOBS,
        'n_events_per_job': N_EVENTS_PER_JOBS,
        'image': SINGULARITY_IMAGE,
        'paraFile': PARAMFILE,
        'job_id': JOBID,
    }

    main(para_dict)

