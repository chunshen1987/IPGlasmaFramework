#!/usr/bin/env python3
"""This script generate all the running jobs."""

import sys
from os import path, mkdir
import shutil
import subprocess
import argparse
from math import ceil
from glob import glob

known_initial_types = [
    "IPGlasma", "IPsat",
]

support_cluster_list = [
    'nersc', 'nerscKNL', 'wsugrid', "OSG", "local", "guillimin", "McGill"
]


def write_script_header(cluster, script, n_threads, event_id, walltime,
                        working_folder):
    """This function write the header of the job submission script"""
    mem = 4*n_threads
    if cluster == "nersc":
        script.write("""#!/bin/bash -l
#SBATCH -p shared
#SBATCH -n 1
#SBATCH -J {0:s}
#SBATCH -t {1:s}
#SBATCH -L SCRATCH
#SBATCH -C haswell
""".format(event_id, walltime))
    elif cluster == "nerscKNL":
        script.write("""#!/bin/bash -l
#SBATCH -p shared
#SBATCH -n 1
#SBATCH -J {0:s}
#SBATCH -t {1:s}
#SBATCH -L SCRATCH
#SBATCH -C knl,quad,cache
""".format(event_id, walltime))
    elif cluster == "guillimin":
        script.write("""#!/usr/bin/env bash
#PBS -N {0:s}
#PBS -l nodes=1:ppn={1:d}
#PBS -l walltime={2:s}
#PBS -S /bin/bash
#PBS -e test.err
#PBS -o test.log
#PBS -A cqn-654-ad
#PBS -q sw
#PBS -d {3:s}
""".format(event_id, n_threads, walltime, working_folder))
    elif cluster == "McGill":
        script.write("""#!/usr/bin/env bash
#PBS -N {0:s}
#PBS -l nodes=1:ppn={1:d}:irulan
#PBS -l walltime={2:s}
#PBS -S /bin/bash
#PBS -e test.err
#PBS -o test.log
#PBS -d {3:s}
""".format(event_id, n_threads, walltime, working_folder))
    elif cluster == "wsugrid":
        script.write("""#!/usr/bin/env bash
#SBATCH --job-name {0:s}
#SBATCH -q primary
#SBATCH -N 1
#SBATCH -n {1:d}
#SBATCH --mem={2:.0f}G
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


def generate_nersc_mpi_job_script(folder_name, n_nodes, n_threads,
                                  n_jobs_per_node, walltime):
    """This function generates job script for NERSC"""
    working_folder = folder_name

    script = open(path.join(working_folder, "submit_MPI_jobs.pbs"), "w")
    script.write("""#!/bin/bash -l
#SBATCH --qos=regular
#SBATCH -N {0:d}
#SBATCH -A m1820
#SBATCH -J music
#SBATCH -t {1:s}
#SBATCH -L SCRATCH
#SBATCH -C haswell
#SBATCH --mail-type=ALL
#SBATCH --mail-user=chunshen1987@gmail.com

export OMP_PROC_BIND=true
export OMP_PLACES=threads

num_of_nodes={0:d}
module load ooops
set_io_param_batch $SLURM_JOBID 0 low
# run all the job
for (( nodeid=1; nodeid <= $num_of_nodes; nodeid++ ))
do
    export OMP_NUM_THREADS={2:d}
    srun -N 1 -n {3:d} -c {2:d} python job_MPI_wrapper.py {3:d} $nodeid &
done
wait
""".format(n_nodes, walltime, n_threads, n_jobs_per_node))
    script.close()


def generate_nerscKNL_mpi_job_script(folder_name, n_nodes, n_threads,
                                     n_jobs_per_node, walltime):
    """This function generates job script for NERSC KNL"""
    working_folder = folder_name

    script = open(path.join(working_folder, "submit_MPI_jobs.pbs"), "w")
    script.write("""#!/bin/bash -l
#SBATCH --qos=regular
#SBATCH -N {0:d}
#SBATCH -A m1820
#SBATCH -J music
#SBATCH -t {1:s}
#SBATCH -L SCRATCH
#SBATCH -C knl,quad,cache
#SBATCH --mail-type=ALL
#SBATCH --mail-user=chunshen1987@gmail.com

export OMP_PROC_BIND=true
export OMP_PLACES=cores

num_of_nodes={0:d}
# run all the job
for (( nodeid=1; nodeid <= $num_of_nodes; nodeid++ ))
do
    export OMP_NUM_THREADS={2:d}
    srun -N 1 -n {3:d} -c {2:d} python job_MPI_wrapper.py {3:d} $nodeid &
done
wait
""".format(n_nodes, walltime, n_threads, n_jobs_per_node))
    script.close()


def generate_full_job_script(cluster_name, folder_name, initial_type,
                             ev0_id, n_ev, n_threads, ipglasma_flag):
    """This function generates full job script"""
    working_folder = folder_name
    event_id = working_folder.split('/')[-1]
    walltime = '100:00:00'

    script = open(path.join(working_folder, "submit_job.pbs"), "w")
    write_script_header(cluster_name, script, n_threads, event_id, walltime,
                        working_folder)
    if cluster_name != "OSG":
        script.write("""
python3 simulation_driver.py {0:s} {1:d} {2:d} {3:d} {4} > run.log
""".format(initial_type, ev0_id, n_ev, n_threads, ipglasma_flag))
    else:
        script.write("""
python3 simulation_driver.py {0:s} {1:d} {2:d} {3:d} {4}
""".format(initial_type, ev0_id, n_ev, n_threads, ipglasma_flag))
    script.close()


def generate_script_ipglasma(folder_name, nthreads, cluster_name, event_id):
    """This function generates script for IPGlasma simulation"""
    working_folder = folder_name

    script = open(path.join(working_folder, "run_ipglasma.sh"), "w")

    results_folder = 'ipglasma_results'
    script.write("""#!/bin/bash

results_folder={0:s}
evid=$1

(
cd ipglasma

mkdir -p $results_folder
rm -fr $results_folder/*

""".format(results_folder))

    if nthreads > 0:
        script.write("""
export OMP_NUM_THREADS={0:d}
""".format(nthreads))

    if cluster_name != "OSG":
        script.write("sleep {}".format(event_id))
        script.write("""
# IPGlasma evolution (run 1 event)
./ipglasma input 1> run.log 2> run.err
""")
    else:
        script.write("""
# IPGlasma evolution (run 1 event)
./ipglasma input
""")
    script.write("""
for ifile in *.dat
do
    filename=$(echo ${ifile} | sed "s/0.dat/${evid}.dat/")
    cat ${ifile} | sed 's$N/A$0.0$g' | sed 's/Q_s/#Q_s/' > $results_folder/${filename}
    rm -fr ${ifile}
done
mv V-* $results_folder/
""")
    if cluster_name != "OSG":
        script.write("""
mv run.log $results_folder/
mv run.err $results_folder/
""")
    script.write(")")
    script.close()


def generate_script_subnucleondiffraction(folder_name, collisionType, event_id,
                                          saveSnapshot, analyzeDiffraction, Low_cut = 0.8, High_cut = 1.2, 
                                          Q21 = 0.0, Q22=33., maxr = 0.5, epslion = 0.1, R_Nuclear = 6.37, with_photon_kT = 1,
                                          OUTPUTAONLY = 1):
    """This function generates script for computing subnucleon diffraction"""
    working_folder = folder_name

    script = open(path.join(working_folder, "run_subnucleondiffraction.sh"),
                  "w")

    results_folder = 'subnucleondiffraction_results'
    script.write("""#!/bin/bash

results_folder={0:s}
evid=$1
fileid=$2
WilsonLineFile=$3


cd subnucleondiffraction

mkdir -p $results_folder

""".format(results_folder))

    if OUTPUTAONLY == 1:
        script.write("""
#### rho ####
for Q2 in {Q21}
do
    GSL_RNG_SEED=$Randum_number ./subnucleondiffraction -dipole 1 ipglasma_binary $WilsonLineFile -maxr {maxr} -epslion {epslion} -OUTPUTAONLY 1 """.format( maxr = maxr, epslion = epslion, Q21 = Q21 ))
        script.write("""-wavef_file gauss-boosted-rho.dat  -real -Q2 ${Q2} -xp 0.01 -mcintpoints 1e4 > $results_folder/rho_Q2_${Q2}_real_${evid}_${fileid}
done""")
        script.write("""
#### rho ####
for Q2 in {Q21}
do
    GSL_RNG_SEED=$Randum_number ./subnucleondiffraction -dipole 1 ipglasma_binary $WilsonLineFile -maxr {maxr} -epslion {epslion} -OUTPUTAONLY 1 """.format( maxr = maxr, epslion = epslion, Q21 = Q21 ))
        script.write("""-wavef_file gauss-boosted-rho.dat  -imag -Q2 ${Q2} -xp 0.01 -mcintpoints 1e4 > $results_folder/rho_Q2_${Q2}_imag_${evid}_${fileid}
done
cd ..""")
        script.close()
        return
    if saveSnapshot:
        script.write("""
./subnucleondiffraction -dipole 1 ipglasma_binary $WilsonLineFile -print_nucleus > ${results_folder}/picture_${evid}_${fileid}

""")
    if analyzeDiffraction > 0:
        script.write("""
# run subnucleon diffraction
((Randum_number=$RANDOM))

""")

        if collisionType == 0:
            # e+P
            if analyzeDiffraction == 2:
                script.write("""
#### rho ####
for Q2 in 3.3 6.6 11.5 17.4 33
do
    GSL_RNG_SEED=$Randum_number ./subnucleondiffraction -dipole 1 ipglasma_binary $WilsonLineFile -mint 0 -maxt 2.5 -wavef_file gauss-boosted-rho.dat -imag -Q2 ${Q2} -mcintpoints 1e6 > $results_folder/rho_Q2_${Q2}_imag_${evid}_${fileid}
    GSL_RNG_SEED=$Randum_number ./subnucleondiffraction -dipole 1 ipglasma_binary $WilsonLineFile -mint 0 -maxt 2.5 -wavef_file gauss-boosted-rho.dat -real -Q2 ${Q2} -mcintpoints 1e6 > $results_folder/rho_Q2_${Q2}_real_${evid}_${fileid}
done
""")
            script.write("""
#### J/Psi ####
# Q^2=0.0
GSL_RNG_SEED=$Randum_number ./subnucleondiffraction -dipole 1 ipglasma_binary $WilsonLineFile -mint 0 -maxt 2.5 -imag -Q2 0.0 -mcintpoints 1e6 > $results_folder/JPsi_Q2_0_imag_${evid}_${fileid}
GSL_RNG_SEED=$Randum_number ./subnucleondiffraction -dipole 1 ipglasma_binary $WilsonLineFile -mint 0 -maxt 2.5 -real -Q2 0.0 -mcintpoints 1e6 > $results_folder/JPsi_Q2_0_real_${evid}_${fileid}

cd ..
""")
        elif collisionType == 1:
            # e+A
            if analyzeDiffraction == 2:
                script.write("""
#### rho ####
for Q2 in 3.3 6.6 11.5 17.4 33
do
    GSL_RNG_SEED=$Randum_number ./subnucleondiffraction -dipole 1 ipglasma_binary $WilsonLineFile -mint 0 -maxt 0.5 -wavef_file gauss-boosted-rho.dat -tstep 0.002 -imag -Q2 ${Q2} -xp 0.001 -mcintpoints 1e6 > $results_folder/rho_Q2_${Q2}_imag_${evid}_${fileid}
    GSL_RNG_SEED=$Randum_number ./subnucleondiffraction -dipole 1 ipglasma_binary $WilsonLineFile -mint 0 -maxt 0.5 -wavef_file gauss-boosted-rho.dat -tstep 0.002 -real -Q2 ${Q2} -xp 0.001 -mcintpoints 1e6 > $results_folder/rho_Q2_${Q2}_real_${evid}_${fileid}
done
""")
            script.write("""
#### J/Psi ####
# Q^2=0.0
GSL_RNG_SEED=$Randum_number ./subnucleondiffraction -dipole 1 ipglasma_binary $WilsonLineFile -mint 0 -maxt 0.5 -tstep 0.002 -imag -Q2 0.0 -xp 0.001 -mcintpoints 1e6 > $results_folder/JPsi_Q2_0_imag_${evid}_${fileid}
GSL_RNG_SEED=$Randum_number ./subnucleondiffraction -dipole 1 ipglasma_binary $WilsonLineFile -mint 0 -maxt 0.5 -tstep 0.002 -real -Q2 0.0 -xp 0.001 -mcintpoints 1e6 > $results_folder/JPsi_Q2_0_real_${evid}_${fileid}

cd ..
""")
        elif collisionType == 2:
            # e+A
            if analyzeDiffraction == 2:
                script.write("""
#### rho ####
for Q2 in {Q21}
do
    GSL_RNG_SEED=$Randum_number ./subnucleondiffraction -dipole 1 ipglasma_binary $WilsonLineFile -maxr {maxr} -epslion {epslion} -DOUPC 1 -UPC_energy 200. -UPC_Nucleus Au -R_Nuclear {R_Nuclear} -DacayToScalarmeson 1 -DOSoftPhoton 0 -mint 0.00005 -maxt1 0.0036 -maxt2 0.05 -maxt3 0.1 -tstep1 0.0002 -tstep2 0.001 -tstep3 0.01 -Low {low} -High {high} """.format(R_Nuclear = R_Nuclear, Q21 = Q21, maxr = maxr, epslion = epslion, low = Low_cut, high = High_cut)) 
                script.write("""-wavef_file gauss-boosted-rho.dat -imag -Q2 ${Q2} -xp 0.001 -mcintpoints 1e6 > $results_folder/rho_Q2_${Q2}_imag_${evid}_${fileid}""")

                script.write("""
    GSL_RNG_SEED=$Randum_number ./subnucleondiffraction -dipole 1 ipglasma_binary $WilsonLineFile -maxr {maxr} -epslion {epslion} -DOUPC 1 -UPC_energy 200. -UPC_Nucleus Au -R_Nuclear {R_Nuclear} -DacayToScalarmeson 1 -DOSoftPhoton 0 -mint 0.00005 -maxt1 0.0036 -maxt2 0.05 -maxt3 0.1 -tstep1 0.0002 -tstep2 0.001 -tstep3 0.01 -Low {low} -High {high} """.format(R_Nuclear = R_Nuclear, maxr = maxr, epslion = epslion, low = Low_cut, high = High_cut)) 
                script.write("""-wavef_file gauss-boosted-rho.dat -real -Q2 ${Q2} -xp 0.001 -mcintpoints 1e6 > $results_folder/rho_Q2_${Q2}_real_${evid}_${fileid}
done""")

                script.write("""
#### J/Psi ####
# Q^2=0.0
GSL_RNG_SEED=$Randum_number ./subnucleondiffraction -dipole 1 ipglasma_binary $WilsonLineFile -maxr {maxr} -DOUPC 1 -UPC_energy 200. -UPC_Nucleus Au -R_Nuclear {R_Nuclear} -DacayToScalarmeson 0 -DOSoftPhoton 0 -mint 0.00005 -maxt1 0.0036 -maxt2 0.05 -maxt3 0.1 -tstep1 0.0002 -tstep2 0.001 -tstep3 0.01 -Low {low} -High {high} """.format(R_Nuclear = R_Nuclear, low = Low_cut, high = High_cut)) 
                script.write("""-imag -Q2 0.0 -xp 0.001 -mcintpoints 1e6 > $results_folder/JPsi_Q2_0_imag_${evid}_${fileid}""")

                script.write("""
GSL_RNG_SEED=$Randum_number ./subnucleondiffraction -dipole 1 ipglasma_binary $WilsonLineFile -maxr {maxr}  -DOUPC 1 -UPC_energy 200. -UPC_Nucleus Au -R_Nuclear {R_Nuclear} -DacayToScalarmeson 0 -DOSoftPhoton 0 -mint 0.00005 -maxt1 0.0036 -maxt2 0.05 -maxt3 0.1 -tstep1 0.0002 -tstep2 0.001 -tstep3 0.01 -Low {low} -High {high} """.format(R_Nuclear = R_Nuclear, low = Low_cut, high = High_cut)) 
                script.write("""-real -Q2 0.0 -xp 0.001 -mcintpoints 1e6 > $results_folder/JPsi_Q2_0_real_${evid}_${fileid}
cd ..""") 
                script.close()
            if analyzeDiffraction == 3:
                script.write("""
#### rho ####
for Q2 in {Q21} 
do
    GSL_RNG_SEED=$Randum_number ./subnucleondiffraction -dipole 1 ipglasma_binary $WilsonLineFile -maxr {maxr} -epslion {epslion} -DOUPC 1 -UPC_energy 200. -UPC_Nucleus Au -R_Nuclear {R_Nuclear} -DacayToScalarmeson 1 -DOSoftPhoton 0 -mint 0.00005 -maxt1 0.0036 -maxt2 0.05 -maxt3 0.1 -tstep1 0.0002 -tstep2 0.001 -tstep3 0.01 -Low {low} -High {high} """.format(R_Nuclear = R_Nuclear, Q21 = Q21, maxr = maxr, epslion = epslion, low = Low_cut, high = High_cut)) 
                script.write("""-wavef_file gauss-boosted-rho.dat -imag -Q2 ${Q2} -xp 0.001 -mcintpoints 1e6 > $results_folder/rho_Q2_${Q2}_imag_${evid}_${fileid}""")

                script.write("""
    GSL_RNG_SEED=$Randum_number ./subnucleondiffraction -dipole 1 ipglasma_binary $WilsonLineFile -maxr {maxr} -epslion {epslion} -DOUPC 1 -UPC_energy 200. -UPC_Nucleus Au -R_Nuclear {R_Nuclear} -DacayToScalarmeson 1 -DOSoftPhoton 0 -mint 0.00005 -maxt1 0.0036 -maxt2 0.05 -maxt3 0.1 -tstep1 0.0002 -tstep2 0.001 -tstep3 0.01 -Low {low} -High {high} """.format(R_Nuclear = R_Nuclear, maxr = maxr, epslion = epslion, low = Low_cut, high = High_cut)) 
                script.write("""-wavef_file gauss-boosted-rho.dat -real -Q2 ${Q2} -xp 0.001 -mcintpoints 1e6 > $results_folder/rho_Q2_${Q2}_real_${evid}_${fileid}
done
cd ..""")

                script.close()
        elif collisionType == 3:
            # e+A for soft radiation for rho only
            if analyzeDiffraction == 2:
                script.write("""
#### rho ####
for Q2 in {Q21}
do
    GSL_RNG_SEED=$Randum_number ./subnucleondiffraction -dipole 1 ipglasma_binary $WilsonLineFile -maxr {maxr} -epslion {epslion} -DOUPC 1 -UPC_energy 200. -UPC_Nucleus Au -R_Nuclear {R_Nuclear} -DacayToScalarmeson 1 -With_photon_kT {with_photon_kT} -DOSoftPhoton 1 -mint 0.0001 -maxt1 0.0036 -maxt2 0.05 -maxt3 0.1 -tstep1 0.0002 -tstep2 0.001 -tstep3 0.01 -Low {low} -High {high} """.format(R_Nuclear = R_Nuclear, maxr = maxr, epslion = epslion, with_photon_kT = with_photon_kT, Q21 = Q21, low = Low_cut, high = High_cut)) 
                script.write("""-wavef_file gauss-boosted-rho.dat -Q2 ${Q2} -xp 0.001 -mcintpoints 1e6 > $results_folder/rho_Q2_${Q2}_imag_${evid}_${fileid}
done
cd ..""")

                script.close()

        elif collisionType == 4:
            # e+A for soft radiation for rho and J/Psi
            if analyzeDiffraction == 3:
                script.write("""
#### rho ####
for Q2 in {Q21}
do
    GSL_RNG_SEED=$Randum_number ./subnucleondiffraction -dipole 1 ipglasma_binary $WilsonLineFile -maxr {maxr} -epslion {epslion} -DOUPC 1 -UPC_energy 200. -UPC_Nucleus Au -R_Nuclear {R_Nuclear} -DacayToScalarmeson 1 -With_photon_kT {with_photon_kT} -DOSoftPhoton 0 -mint 0.0001 -maxt1 0.0036 -maxt2 0.05 -maxt3 0.1 -tstep1 0.0002 -tstep2 0.001 -tstep3 0.01 -Low {low} -High {high} """.format(R_Nuclear = R_Nuclear, maxr = maxr, epslion = epslion, with_photon_kT = with_photon_kT, Q21 = Q21, low = Low_cut, high = High_cut)) 
                script.write("""-wavef_file gauss-boosted-rho.dat -Q2 ${Q2} -xp 0.001 -mcintpoints 1e3 > $results_folder/rho_Q2_${Q2}_imag_${evid}_${fileid}
done
cd ..""")

                script.close()
def generate_event_folders(initial_condition_type, collisionType,
                           package_root_path, code_path, working_folder,
                           cluster_name, event_id, event_id_offset,
                           n_ev, n_threads, save_ipglasma_flag, saveSnapshot,
                           analyzeDiffraction, Low_cut, High_cut, Q21, Q22, maxr,
                           epslion, R_Nuclear, with_photon_kT, OUTPUTAONLY):
    """This function creates the event folder structure"""
    event_folder = path.join(working_folder, 'event_%d' % event_id)
    param_folder = path.join(working_folder, 'model_parameters')
    mkdir(event_folder)
    shutil.copy(path.join(code_path, 'simulation_driver.py'),
                event_folder)
    if initial_condition_type in ("IPGlasma"):
        generate_script_ipglasma(event_folder, n_threads, cluster_name,
                                 event_id)
        mkdir(path.join(event_folder, 'ipglasma'))
        shutil.copyfile(path.join(param_folder, 'IPGlasma/input'),
                        path.join(event_folder, 'ipglasma/input'))
        link_list = [
            'qs2Adj_vs_Tp_vs_Y_200.in', 'utilities', 'ipglasma',
            'nucleusConfigurations'
        ]
        for link_i in link_list:
            subprocess.call("ln -s {0:s} {1:s}".format(
                path.abspath(path.join(code_path,
                                       'ipglasma_code/{}'.format(link_i))),
                path.join(event_folder, "ipglasma/{}".format(link_i))),
                shell=True)

        # subnucleondiffraction
        mkdir(path.join(event_folder, 'subnucleondiffraction'))
        generate_script_subnucleondiffraction(event_folder, collisionType,
                                              event_id, saveSnapshot,
                                              analyzeDiffraction, Low_cut, High_cut, Q21, Q22, 
                                              maxr, epslion, R_Nuclear, with_photon_kT, OUTPUTAONLY)
        link_list = ['build/bin/subnucleondiffraction', 'gauss-boosted.dat',
                     'gauss-boosted-rho.dat']
        for link_i in link_list:
            subprocess.call("ln -s {0:s} {1:s}".format(
                path.abspath(path.join(
                    code_path, 'subnucleondiffraction_code/{}'.format(link_i))),
                path.join(event_folder,
                          "subnucleondiffraction/{}".format(
                                                    link_i.split("/")[-1]))),
                shell=True)

    generate_full_job_script(cluster_name, event_folder,
                             initial_condition_type,
                             event_id_offset, n_ev, n_threads,
                             save_ipglasma_flag)


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
        description='\U0000269B Welcome to the IPGlasmaFramework',
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
                        '--n_events',
                        metavar='',
                        type=int,
                        default=1,
                        help='number of events per job')
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
                        default='parameters_dict_user.py',
                        help='user-defined parameter dictionary file')
    parser.add_argument('-b',
                        '--bayes_file',
                        metavar='',
                        type=str,
                        default='',
                        help='parameters from bayesian analysis')
    parser.add_argument('-id',
                        '--OSG_process_id',
                        metavar='',
                        type=int,
                        default='0',
                        help='OSG job process id number')
    parser.add_argument('-seed',
                        '--random_seed',
                        metavar='',
                        type=int,
                        default='-1',
                        help='Random Seed (-1: according to system time)')
    parser.add_argument('--copy', action='store_true')
    parser.add_argument("--continueFlag", action="store_true")
    args = parser.parse_args()

    if len(sys.argv) < 2:
        parser.print_help()
        exit(0)

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
        n_ev = args.n_events
        n_threads = args.n_threads
        osg_job_id = args.OSG_process_id
        seed = args.random_seed
    except:
        parser.print_help()
        exit(0)

    code_package_path = path.abspath(path.dirname(__file__))

    par_diretory = path.dirname(path.abspath(args.par_dict))
    sys.path.insert(0, par_diretory)
    parameter_dict = __import__(args.par_dict.split('.py')[0].split("/")[-1])

    if cluster_name == "OSG":
        if seed == -1:
            seed = 0
        seed += osg_job_id
        print("seed = ", seed)
        args.nocopy = True

    initial_condition_type = (
            parameter_dict.control_dict['initial_state_type'])
    if initial_condition_type not in known_initial_types:
        print("\U0001F6AB  "
              + "Do not recognize the initial condition type: {}".format(
                  initial_condition_type))
        exit(1)

    collisionType = 0
    if (parameter_dict.ipglasma_dict['Projectile']
            == parameter_dict.ipglasma_dict['Target']):
        if parameter_dict.ipglasma_dict['Projectile'] != "p":
            collisionType = 1
    else:
        print("\U0001F6AB  "
                + "Projectile and Target species are different! Proj: "
                + parameter_dict.ipglasma_dict['Projectile']
                + ", target : "
                + parameter_dict.ipglasma_dict['Target']
        )
        exit(1)

    if (parameter_dict.ipglasma_dict['DO_UPC_DIFF'] == 1):
        collisionType = 2

        collisionType = int(collisionType) + int(parameter_dict.ipglasma_dict['DO_SOFT_RAD'])
        if (parameter_dict.control_dict['with_photon_kT'] == 1):
            collisionType = int(collisionType) + 2
    working_folder_name = path.abspath(working_folder_name)
    if path.exists(working_folder_name) and args.continueFlag:
        return

    create_a_working_folder(working_folder_name)

    shutil.copy(args.par_dict, working_folder_name)
    code_path = path.join(code_package_path, "codes")
    if args.copy:
        code_path = path.join(working_folder_name, "codes")
        shutil.copytree("{}/codes".format(code_package_path), code_path)

    if args.bayes_file != "":
        args.bayes_file = path.join(path.abspath("."), args.bayes_file)
        subprocess.call("(cd {}/config; ".format(code_package_path)
                        + "python3 parameters_dict_master.py "
                        + "-path {} -par {} -b {} -seed {};)".format(
                            working_folder_name, path.abspath(args.par_dict),
                            args.bayes_file, seed),
                        shell=True)
        shutil.copy(args.bayes_file, working_folder_name)
    else:
        subprocess.call(
            "(cd {}/config; ".format(code_package_path)
            + "python3 parameters_dict_master.py "
            + "-path {} -par {} -seed {};)".format(
                working_folder_name, path.abspath(args.par_dict), seed),
            shell=True)

    toolbar_width = 40
    sys.stdout.write("\U0001F375  Generating {} jobs [{}]".format(
        n_jobs, " "*toolbar_width))
    sys.stdout.flush()
    sys.stdout.write("\b"*(toolbar_width + 1))
    event_id_offset = osg_job_id
    for ijob in range(n_jobs):
        progress_i = (int(float(ijob + 1)/n_jobs*toolbar_width)
                      - int(float(ijob)/n_jobs*toolbar_width))
        for ii in range(progress_i):
            sys.stdout.write("#")
            sys.stdout.flush()
        if cluster_name == "OSG":
            event_id_offset = osg_job_id*n_ev
        save_ipglasma_flag = False
        if initial_condition_type in ("IPGlasma"):
            save_ipglasma_flag = (
                    parameter_dict.control_dict['save_ipglasma_results'])
        saveSnapshot = parameter_dict.control_dict['saveNucleusSnapshot']
        analyzeDiffraction = parameter_dict.control_dict['analyzeDiffraction']
        Low_cut = parameter_dict.control_dict['Low_cut']
        High_cut = parameter_dict.control_dict['High_cut']
        Q21 = parameter_dict.control_dict['Q21']
        Q22 = parameter_dict.control_dict['Q22']
        maxr = parameter_dict.control_dict['maxr']
        epslion = parameter_dict.control_dict['epslion']
        with_photon_kT = parameter_dict.control_dict['with_photon_kT']
        OUTPUTAONLY = parameter_dict.control_dict['OUTPUT_A_ONLY']
        R_Nuclear = parameter_dict.ipglasma_dict['R_WS']
        generate_event_folders(initial_condition_type, collisionType,
                               code_package_path, code_path,
                               working_folder_name, cluster_name,
                               ijob, event_id_offset, n_ev, n_threads,
                               save_ipglasma_flag, saveSnapshot,
                               analyzeDiffraction, Low_cut, High_cut, Q21, Q22, 
                               maxr, epslion, R_Nuclear, with_photon_kT, OUTPUTAONLY)
        event_id_offset += n_ev
    sys.stdout.write("\n")
    sys.stdout.flush()

    pwd = path.abspath(".")
    script_path = path.join(code_package_path, "utilities")
    shutil.copy(path.join(script_path, 'collect_events.sh'), pwd)
    shutil.copy(path.join(script_path, 'combine_multiple_hdf5.py'), pwd)
    walltime = '10:00:00'
    if "walltime" in parameter_dict.control_dict.keys():
        walltime = parameter_dict.control_dict["walltime"]
    if cluster_name == "nersc":
        shutil.copy(
            path.join(code_package_path,
                      'Cluster_supports/NERSC/job_MPI_wrapper.py'),
            working_folder_name)
        n_nodes = max(1, int(n_jobs*n_threads/64))
        generate_nersc_mpi_job_script(working_folder_name, n_nodes, n_threads,
                                      int(n_jobs/n_nodes), walltime)

    if cluster_name == "nerscKNL":
        shutil.copy(
            path.join(code_package_path,
                      'Cluster_supports/NERSC/job_MPI_wrapper.py'),
            working_folder_name)
        n_nodes = max(1, int(n_jobs*n_threads/272))
        generate_nerscKNL_mpi_job_script(working_folder_name, n_nodes,
                                         n_threads, int(n_jobs/n_nodes),
                                         walltime)

    if cluster_name == "wsugrid":
        shutil.copy(
            path.join(code_package_path,
                      'Cluster_supports/WSUgrid/submit_all_jobs.sh'), pwd)


if __name__ == "__main__":
    main()

