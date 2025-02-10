#!/usr/bin/env bash

workFolder=$1
parafile=$2
processId=$3
nEvents=$4
nthreads=$5
seed=$6
bayesFile=$7


# Run the singularity container
export PYTHONIOENCODING=utf-8
export PATH="${PATH}:/usr/lib64/openmpi/bin:/usr/local/gsl/2.5/x86_64/bin"
export LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:/usr/local/lib:/usr/local/gsl/2.5/x86_64/lib64"

printf "Start time: `/bin/date`\n"
printf "Job is running on node: `/bin/hostname`\n"
printf "system kernel: `uname -r`\n"
printf "Job running as user: `/usr/bin/id`\n"

if [ -z ${bayesFile} ]
then
    /opt/IPGlasmaFramework/generate_jobs.py -w ${workFolder} -c wsugrid -par ${parafile} -id ${processId} -n_ev ${nEvents} -n_th ${nthreads} -seed ${seed} --continueFlag
else
    /opt/IPGlasmaFramework/generate_jobs.py -w ${workFolder} -c wsugrid -par ${parafile} -id ${processId} -n_ev ${nEvents} -n_th ${nthreads} -seed ${seed} -b ${bayesFile} --continueFlag
fi


cd ${workFolder}/event_0
bash submit_job.script
status=$?
if [ $status -ne 0 ]; then
    exit $status
fi
