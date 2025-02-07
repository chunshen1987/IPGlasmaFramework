#!/usr/bin/env python3
"""
    This script contains all the default parameters in the iEBE-MUSIC package.
"""

from os import path, makedirs
import sys
import shutil
import argparse

# control parameters
control_dict = {
    'initial_state_type': "IPGlasma",  # options: IPGlasma, IPsat
    'walltime': "10:00:00",            # walltime to run
    'save_ipglasma_results': False,    # flag to save IPGlasma results
}


# IPGlasma
ipglasma_dict = {
    'mode': 1,  # run mode
    'readMultFromFile': 0,
    'size': 720,  # number of grid points of IP-Glasma computation
    'L': 20.,  # grid size in the transverse plane
    'Nc': 3,  # number of color
    'm': 0.2,  # infrared cut-off mass (GeV)
    'rmax': 1000.,
    'UVdamp': 0.,
    'Jacobianm': 0.35,
    'g': 1.,  # strong coupling constant
    'SubNucleonParamType': 0,  # 0: do not use posterior parameter sets
    # 1: use subnucleon parameters from variant Nq posterior distribution
    # 2: use subnucleon parameters from fixed Nq = 3 posterior distribution
    'SubNucleonParamSet':
        -1,  # -1: choose a random set from the posterior distribution
    # 0: choose the MAP parameter set
    # positive intergers: choose a fixed set of parameter for sub-nucleonic structure
    'BG': 4.,
    'BGq': 0.3,
    'BGqVar': 0.0,
    'dqMin': 0.0,
    'useSmoothNucleus': 0,
    'useConstituentQuarkProton': 0,
    'NqFluc': 0.0,
    'shiftConstituentQuarkProtonOrigin': 1,
    'runningCoupling': 0,
    'muZero': 0.3,
    'minimumQs2ST': 0.,
    'setWSDeformParams': 0,
    'R_WS': 6.6,
    'a_WS': 0.52,
    'dR_np': 0.,
    'da_np': 0.,
    'beta2': 0.28,
    'beta3': 0.0,
    'beta4': 0.0,
    'gamma': 0.0,
    'force_dmin_flag': 1,  # flag to force d_min for deformed nuclei
    'd_min': 0.9,  # fm
    'c': 0.2,
    'g2mu': 0.1,
    'useFatTails': 0,
    'tDistNu': 3,
    'smearQs': 1,
    'smearingWidth': 0.6,
    'protonAnisotropy': 0,
    'roots': 200.,
    'usePseudoRapidity': 0,
    'Rapidity': 0.,
    'useFluctuatingx': 0,
    'xFromThisFactorTimesQs': 1,
    'useNucleus': 1,
    'useGaussian': 0,
    'nucleonPositionsFromFile': 0,
    'NucleusQsTableFileName': "qs2Adj_vs_Tp_vs_Y_200.in",
    'QsmuRatio': 0.8,
    'samplebFromLinearDistribution': 1,
    'runWith0Min1Avg2MaxQs': 2,
    'runWithThisFactorTimesQs': 0.5,
    'runWithLocalQs': 0,
    'runWithkt': 0,
    'Ny': 50,
    'useSeedList': 0,
    'seed': 3,
    'useTimeForSeed': 0,
    'Projectile': "Au",
    'Target': "Au",
    'bmin': 0.,
    'bmax': 0.,
    'rotateReactionPlane': 0,
    'lightNucleusOption': 1,
    'useFixedNpart': 0,
    'averageOverThisManyNuclei': 1,
    'SigmaNN': 42.,
    'gaussianWounding': 1,
    'inverseQsForMaxTime': 0,
    'maxtime': 0.4,
    'dtau': 0.1,
    'LOutput': 30,
    'sizeOutput': 512,
    'computeGluonMultiplicity': 0,
    'etaSizeOutput': 1,
    'detaOutput': 0,
    'writeOutputs': 0,
    'writeEvolution': 0,
    'readInitialWilsonLines': 0,
    'writeInitialWilsonLines': 1,
    'writeOutputsToHDF5': 0,
    'useJIMWLK': 0,
    'mu0_jimwlk': 0.28,
    'simpleLangevin': 1,
    'alphas_jimwlk': 0,
    'jimwlk_ic_x': 0.01,
    'x_projectile_jimwlk': 0.001,
    'x_target_jimwlk': 0.001,
    'Ds_jimwlk': 0.005,
    'Lambda_QCD_jimwlk': 0.040,
    'm_jimwlk': 0.4,
}


Parameters_list = [
    (ipglasma_dict, "input", 3),
]

path_list = [
    'model_parameters/IPGlasma/',
]


def update_parameters_dict(par_dict_path, ran_seed):
    """This function update the parameters dictionaries with user's settings"""
    par_diretory = path.dirname(par_dict_path)
    sys.path.insert(0, par_diretory)
    print(par_diretory)
    parameters_dict = __import__(par_dict_path.split('.py')[0].split('/')[-1])
    initial_condition_type = (
                    parameters_dict.control_dict['initial_state_type'])
    if initial_condition_type in ("IPGlasma"):
        ipglasma_dict.update(parameters_dict.ipglasma_dict)

        # set random seed
        if ran_seed == -1:
            ipglasma_dict['useTimeForSeed'] = 1
        else:
            ipglasma_dict['seed'] = ran_seed


def update_parameters_bayesian(bayes_file):
    parfile = open(bayes_file, "r")
    for line in parfile:
        key, val = line.split()
        if key in ipglasma_dict.keys():
            ipglasma_dict[key] = float(val)


def output_parameters_to_files(workfolder="."):
    """This function outputs parameters in dictionaries to files"""
    workfolder = path.abspath(workfolder)
    print("\U0001F375  Output input parameter files to {}...".format(
                                                                workfolder))
    for idict, (parameters_dict, fname, itype) in enumerate(Parameters_list):
        output_folder = path.join(workfolder, path_list[idict])
        if not path.exists(output_folder):
            makedirs(output_folder)
        f = open(path.join(output_folder, fname), "w")
        for key_name in parameters_dict:
            if itype in (0, 2):
                f.write("{parameter_name}  {parameter_value}\n".format(
                    parameter_name=key_name,
                    parameter_value=parameters_dict[key_name]))
            elif itype == 1:
                f.write("{parameter_name} = {parameter_value}\n".format(
                    parameter_name=key_name,
                    parameter_value=parameters_dict[key_name]))
            elif itype == 3:
                if key_name in ("type", "database_name_pattern"): continue
                f.write("{parameter_name}  {parameter_value}\n".format(
                    parameter_name=key_name,
                    parameter_value=parameters_dict[key_name]))
            elif itype == 4:
                f.write("[{}]\n".format(key_name))
                for subkey_name in parameters_dict[key_name]:
                    f.write("{parameter_name} = {parameter_value}\n".format(
                        parameter_name=subkey_name,
                        parameter_value=parameters_dict[key_name][subkey_name])
                    )
        if itype == 2:
            f.write("EndOfData")
        elif itype == 3:
            f.write("EndOfFile")
        f.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            description='\U0000269B Welcome to iEBE-MUSIC parameter master',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-path', '--path', metavar='',
                        type=str, default='.',
                        help='output folder path')
    parser.add_argument('-par', '--par_dict', metavar='',
                        type=str, default='parameters_dict_user',
                        help='user-defined parameter dictionary filename')
    parser.add_argument('-b', '--bayes_file', metavar='',
                        type=str, default='',
                        help='parameters from bayesian analysis')
    parser.add_argument('-seed', '--random_seed', metavar='',
                        type=int, default=-1,
                        help='input random seed')
    args = parser.parse_args()
    update_parameters_dict(path.abspath(args.par_dict), args.random_seed)
    if args.bayes_file != "":
        update_parameters_bayesian(args.bayes_file)
    output_parameters_to_files(args.path)
