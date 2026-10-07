#!/usr/bin/env python3
"""
    This script contains all the user modified parameters in
    the IPGlasmaFramework package.
"""

# control parameters
control_dict = {
    'initial_state_type': "IPGlasma",
    'walltime': "10:00:00",             # walltime to run
    'save_ipglasma_results': False,     # flag to save the Wilson lines
    'usePosteriorParameters': True,     # flag to use posterior parameters
    'PosteriorChainFilePath': "config/arXiv_2507.14087/Posterior_wK",
    'PosteriorParamSet': 0,
}


# IPGlasma
ipglasma_dict = {
    'mode': 2,          # run mode (generate Wilson line for nuclei)
    'L': 18.,           # grid size in the transverse plane
    'size': 720,        # number of grid points of IP-Glasma computation
    'LOutput': 18.,
    'sizeOutput': 720,
    'm': 0.4,
    'BG': 3.,
    'BGq': 0.3,
    'omega': 1.0,
    'nucleonModel': "hotspots",   # gaussian: round proton; hotspots: fluctuating proton
    'Nq': 3,                        # number of hot spots
    'smearingWidth': 0.6,
    'QsMuRatio': 0.7,
    'useFluctuatingX': 0,
    'sqrtS': 200.,
    'sigmaNN': 42.,
    'projectile': "Pb",
    'target': "Pb",
    'useRandomSeed': 1,
    'useJIMWLK': 1,
    'jimwlkMu0': 0.28,
    'jimwlkAlphaS': 0,
    'jimwlkInitialX': 0.01,                        # W = 31 GeV (J/Psi, Q^2 = 0)
    'projectileX': 1.45374716e-05,      # W = 813.05 GeV (J/Psi, Q^2 = 0)
    'targetX': 1.45374716e-05,          # W = 813.05 GeV (J/Psi, Q^2 = 0)
    'jimwlkDs': 0.005,
    'jimwlkLambdaQCD': 0.040,
    'jimwlkMass': 0.4,
    'jimwlkSaveSnapshots': 1,
    'jimwlkXSnapshotList': [4.56139851e-03, 6.18101984e-04, 6.51719835e-05],  # W = 45.9, 124.69, 384 GeV (J/Psi, Q^2 = 0)
    'writeWilsonLines': 2,      # 2: binary
}

diffraction_dict = {
    'computeTotalCrossSection': 1,
    'analyzeDiffraction': 0,                # mode 1: JPsi
    'saveNucleusSnapshot': False,           # flag to save the trace of Wilson Line distribution
    "wavef_model": 'boostedgaussian',       # "gauslc"
    "wavef_file": 'gauss-boosted.dat',      # "gaus-lc.dat"
    "mcintpoints": 100000,                  # "auto"
    "maxb": 51.,                            # GeV^-1
    "nbperp": 25,
    "ntheta": 32,                           # theta grid of the total cross section; not in the published setup, which predates it
    # t values [GeV^2]: tlist if it is given, otherwise mint to maxt (inclusive) in steps of tstep
    "mint": 0.0,
    "maxt": 1.0,
    "tstep": 0.1,
    "tlist": [0.0, 0.001, 0.003, 0.005, 0.008, 0.01, 0.02, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5],
    "Q2List": [0.0,],
}
