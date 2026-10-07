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
    'usePosteriorParameters': False,   # flag to use posterior parameters
    'PosteriorChainFilePath': "config/arXiv_2507.14087/Posterior_wK",
    'PosteriorParamSet': 0,
}


# IPGlasma (input keys of IP-Glasma 2.0, in the order of its parameter table;
# keys whose feature is switched off are accepted and ignored by IP-Glasma)
ipglasma_dict = {
    'mode': 2,          # run mode (generate Wilson line for nuclei)
    'size': 720,  # number of grid points of IP-Glasma computation
    'L': 20.,  # grid size in the transverse plane
    'Ny': 50,
    'sqrtS': 200.,
    'g': 1.,  # strong coupling constant
    'maxTime': 0.0,
    'inverseQsForMaxTime': 0,
    'seed': 3,
    'useSeedList': 0,
    'useRandomSeed': 0,
    'projectile': "Au",
    'target': "Au",
    'sigmaNN': 42.,
    'bMin': 0.,
    'bMax': 0.,
    'sampleBFromLinearDistribution': 1,
    'rotateReactionPlane': 0,
    'useNucleus': 1,
    'useSmoothNucleus': 0,
    'useFixedNpart': 0,
    'nucleiToAverage': 1,
    'gaussianWounding': 1,
    'nucleonPositionsFromFile': 0,
    'lightNucleusOption': 1,
    'polarizationProjectile': 0,    # 0: unpolarized; 1: longitudinal polarized; 2: transverse polarized
    'polarizationTarget': 0,        # 0: unpolarized; 1: longitudinal polarized; 2: transverse polarized
    'polarizationProjectileJz': 0,
    'polarizationTargetJz': 0,
    'useInputWSParams': 0,
    'radiusWS': 6.6,
    'diffusenessWS': 0.52,
    'beta2': 0.28,
    'beta3': 0.0,
    'beta4': 0.0,
    'gamma': 0.0,
    'deltaRnp': 0.,
    'deltaAnp': 0.,
    'forceDMin': 1,  # flag to force dMin for deformed nuclei
    'dMin': 0.9,  # fm
    'nucleonModel': "gaussian",     # gaussian, hotspots or strings
    'subNucleonParamType': 0,  # 0: do not use posterior parameter sets
    # 1: use subnucleon parameters from variant Nq posterior distribution
    # 2: use subnucleon parameters from fixed Nq = 3 posterior distribution
    'subNucleonParamSet':
        -1,  # -1: choose a random set from the posterior distribution
    # 0: choose the MAP parameter set
    # positive intergers: choose a fixed set of parameter for sub-nucleonic structure
    'm': 0.2,  # infrared cut-off mass (GeV)
    'BG': 4.,
    'protonAnisotropy': 0,
    'BGq': 0.3,
    'BGqVar': 0.0,
    'dqMin': 0.0,
    'omega': 1.0,
    'Nq': 3,                        # number of hot spots (nucleonModel hotspots)
    'NqFluc': 0.0,
    'shiftConstituentQuarkProtonOrigin': 1,
    'QsMuRatio': 0.8,
    'smearQs': 1,
    'smearingWidth': 0.6,
    'UVDamp': 0.,
    'minimumQs2ST': 0,
    'nucleusQsTableFileName': "qs2Adj_vs_Tp_vs_Y_240.in",
    'rapidity': 0.,                 # rapidity of the gluon and hadron spectra
    'usePseudoRapidity': 0,
    'jacobianMass': 0.35,
    'useFluctuatingX': 0,
    'projectileX': 0.01,            # Bjorken x of the projectile (final x with JIMWLK)
    'targetX': 0.01,                # Bjorken x of the target (final x with JIMWLK)
    'xQsFactor': 1,
    'runningCoupling': 0,
    'mu0': 0.3,
    'c': 0.2,
    'runWithQs': 2,
    'runningCouplingQsFactor': 0.5,
    'runWithLocalQs': 0,
    'runWithKt': 0,
    'computeGluonMultiplicity': 0,
    'computeEccentricities': 0,
    'writeHydro': 0,
    'writeJazma': 0,
    'writeTmunu': 0,
    'writeOutputsToHDF5': 0,
    'LOutput': 30,
    'sizeOutput': 512,
    'etaSizeOutput': 1,
    'dEtaOutput': 0,
    'writeWilsonLines': 1,
    'writeWilsonLineGeometry': 0,   # only needed to read the Wilson lines back in
    'readInitialWilsonLines': 0,
    'useJIMWLK': 0,
    'jimwlkMu0': 0.28,
    'jimwlkLambdaQCD': 0.040,
    'jimwlkMass': 0.4,
    'jimwlkAlphaS': 0,
    'jimwlkDs': 0.005,
    'jimwlkInitialX': 0.01,
    'jimwlkSaveSnapshots': 0,
    'jimwlkXSnapshotList': [0.005,0.001,0.0005,0.0001,0.00005,0.00001],
}


Parameters_list = [
    (ipglasma_dict, "input", 3),
]

path_list = [
    'model_parameters/IPGlasma/',
]


def update_parameters_dict(par_dict_path, ran_seed) -> None:
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
            ipglasma_dict['useRandomSeed'] = 1
        else:
            ipglasma_dict['seed'] = ran_seed


def update_parameters_bayesian(bayes_file) -> None:
    parfile = open(bayes_file, "r")
    for line in parfile:
        key, val = line.split()
        if key in ipglasma_dict.keys():
            ipglasma_dict[key] = float(val)


def output_parameters_to_files(workfolder=".") -> None:
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
                if isinstance(parameters_dict[key_name], list):
                    if parameters_dict[key_name] != []:
                        varStr = ",".join(
                            [str(var) for var in parameters_dict[key_name]])
                        f.write(f"{key_name}  {varStr}\n")
                else:
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
