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
    'runEvolution': 0,  # 0: only build (and JIMWLK-evolve) and write the Wilson lines
    'size': 720,  # number of grid points of IP-Glasma computation
    'L': 20.,  # grid size in the transverse plane
    'Ny': 50,
    'sqrtS': 200.,
    'g': 1.,  # strong coupling constant
    'maxTime': 0.0,
    'inverseQsForMaxTime': 0,
    'seed': 0,          # set by generate_jobs.py -seed; -1 draws a random seed
    'useSeedList': 0,
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
    'writeWilsonLines': 2,          # 2: binary, which run_subnucleondiffraction.sh reads (1: text)
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


# Parameters set by the user dictionary or by a parameter file (not by the
# defaults above), with where they were set
explicit_parameters = {}


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
        for key in parameters_dict.ipglasma_dict:
            explicit_parameters[key] = "the user dictionary"

        # set random seed
        # random seed (-1) unless one is given and the user dictionary
        # does not ask for a random seed
        if ran_seed == -1 or ipglasma_dict['seed'] == -1:
            ipglasma_dict['seed'] = -1
        else:
            ipglasma_dict['seed'] = ran_seed


# Posterior parameter files (written by parameterGenerator.py, or passed to
# generate_jobs.py with -b) may use the names of IP-Glasma before 2.0
posterior_key_names = {
    'QsmuRatio': 'QsMuRatio',
    'm_jimwlk': 'jimwlkMass',
    'Lambda_QCD_jimwlk': 'jimwlkLambdaQCD',
    'UVdamp': 'UVDamp',
    'useConstituentQuarkProton': 'Nq',
}

# Values in the posterior parameter files that are not IP-Glasma parameters
posterior_non_ipglasma_keys = ('Kfactor',)

# Subnucleon parameters each nucleonModel reads in IP-Glasma 5b729ce
# (src/ParameterTable.cpp); the others are ignored without a message
nucleon_model_parameters = {
    'gaussian': ('BG', 'protonAnisotropy', 'smearQs', 'smearingWidth'),
    'hotspots': ('BG', 'BGq', 'BGqVar', 'dqMin', 'omega', 'Nq', 'NqFluc',
                 'shiftConstituentQuarkProtonOrigin', 'smearQs',
                 'smearingWidth'),
    'strings': ('BG', 'BGq', 'BGqVar', 'dqMin', 'omega',
                'shiftConstituentQuarkProtonOrigin', 'smearQs',
                'smearingWidth'),
}
subnucleon_parameters = sorted(
    set().union(*nucleon_model_parameters.values()))

# With subNucleonParamType != 0, IP-Glasma replaces these values with a
# posterior set at run time (Parameters::setParamsWithPosteriorParameterSet)
# and sets BGqVar and NqFluc to 0
posterior_replaced_parameters = (
    'm', 'BG', 'BGq', 'smearingWidth', 'Nq', 'QsMuRatio', 'dqMin')
posterior_zeroed_parameters = ('BGqVar', 'NqFluc')


def check_nucleon_model() -> str:
    """Returns the nucleonModel to write; stops if IP-Glasma does not know
    it."""
    model = ipglasma_dict['nucleonModel']
    if model not in nucleon_model_parameters:
        sys.exit("\U0001F6AB  Unknown nucleonModel {}: use gaussian, "
                 "hotspots or strings.".format(model))
    return model


def check_nq_from_parameter_file(nq, bayes_file) -> bool:
    """Checks the number of hot spots Nq of a parameter file against the
    nucleonModel of the user dictionary (or the default), which a parameter
    file never changes. Returns whether Nq is to be set; stops on a
    conflict."""
    model = check_nucleon_model()
    if model == "hotspots" and nq > 0:
        return True
    if model == "strings" and nq == 3:
        # IP-Glasma does not read Nq with strings: always three hot spots
        return True
    if model == "gaussian" and nq <= 0:
        return False

    if explicit_parameters.get('nucleonModel') == "the user dictionary":
        model_origin = "set in the user dictionary"
    else:
        model_origin = ("the default of parameters_dict_master.py, since the "
                        "user dictionary does not set it")
    if model == "gaussian":
        conflict = ("the parameter file describes {:g} hot spots, but "
                    "gaussian nucleons have none".format(nq))
    elif nq <= 0:
        conflict = ("Nq {:g} (useConstituentQuarkProton 0 before IP-Glasma "
                    "2.0) describes round Gaussian nucleons, but {} nucleons "
                    "have hot spots".format(nq, model))
    else:
        conflict = ("strings nucleons always have 3 hot spots, but the "
                    "parameter file asks for {:g}".format(nq))
    message = (
        "\U0001F6AB  Nq {:g} in the parameter file {} does not fit "
        "nucleonModel {} ({}): {}.\n".format(nq, bayes_file, model,
                                             model_origin, conflict)
        + "    Set 'nucleonModel' in the ipglasma_dict of the user "
        "dictionary to the model you intend (gaussian, hotspots or "
        "strings). Parameter files no longer choose the nucleon model: "
        "before, Nq > 0 in a parameter file switched to hotspots, and "
        "Nq <= 0 to gaussian, whatever the user dictionary said.")
    sys.exit(message)


def update_parameters_bayesian(bayes_file) -> None:
    unknown_keys = []
    with open(bayes_file, "r") as parfile:
        for line in parfile:
            if line.strip() == "":
                continue
            key, val = line.split()
            if key in posterior_non_ipglasma_keys:
                continue
            key = posterior_key_names.get(key, key)
            if key == 'nucleonModel':
                sys.exit("\U0001F6AB  The parameter file {} sets "
                         "nucleonModel. Choose the nucleon model in the "
                         "user dictionary instead.".format(bayes_file))
            if key not in ipglasma_dict:
                unknown_keys.append(key)
                continue
            if key == 'Nq' and not check_nq_from_parameter_file(
                    float(val), bayes_file):
                continue
            ipglasma_dict[key] = float(val)
            explicit_parameters[key] = "the parameter file"
    if unknown_keys:
        sys.exit("\U0001F6AB  Unknown parameters in {}: {}".format(
            bayes_file, ", ".join(unknown_keys)))


def warn_about_subnucleon_parameters() -> None:
    """Warns about subnucleon parameters that the user dictionary or the
    parameter file set, but that IP-Glasma does not use: the chosen
    nucleonModel does not read them, or a posterior set replaces them."""
    model = check_nucleon_model()
    for key in subnucleon_parameters:
        if key not in explicit_parameters:
            continue
        if key in nucleon_model_parameters[model]:
            continue
        if model == "strings" and key == 'Nq' and ipglasma_dict[key] == 3:
            continue
        print("\u26A0\uFE0F  {} {} is set in {}, but nucleonModel {} does "
              "not read it".format(key, ipglasma_dict[key],
                                   explicit_parameters[key], model))

    if ipglasma_dict['subNucleonParamType'] != 0:
        replaced = [key for key in posterior_replaced_parameters
                    if key in explicit_parameters]
        zeroed = [key for key in posterior_zeroed_parameters
                  if key in explicit_parameters]
        if replaced or zeroed:
            message = ("\u26A0\uFE0F  subNucleonParamType {}: IP-Glasma "
                       "uses a posterior parameter set".format(
                           ipglasma_dict['subNucleonParamType']))
            if replaced:
                message += ", which replaces the values of {}".format(
                    ", ".join(replaced))
            if zeroed:
                message += "{} sets {} to 0".format(
                    ", and" if replaced else ", which",
                    ", ".join(zeroed))
            print(message)


def print_nucleon_model() -> None:
    """Prints the nucleon model that is written to the input file, with the
    subnucleon parameters it reads."""
    model = check_nucleon_model()
    print("\U0001F535  nucleonModel {}: {}".format(
        model, ", ".join("{} {}".format(key, ipglasma_dict[key])
                         for key in nucleon_model_parameters[model])))


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
    warn_about_subnucleon_parameters()
    print_nucleon_model()
    output_parameters_to_files(args.path)
