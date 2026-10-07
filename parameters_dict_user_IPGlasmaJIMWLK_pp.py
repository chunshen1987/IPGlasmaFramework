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
}


# IPGlasma
ipglasma_dict = {
    'mode': 2,          # run mode (generate Wilson line for nuclei)
    'L': 5.12,          # grid size in the transverse plane
    'size': 720,        # number of grid points of IP-Glasma computation
    'LOutput': 5.12,
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
    'projectile': "p",
    'target': "p",
    'useRandomSeed': 1,
    'useJIMWLK': 1,
    'jimwlkMu0': 0.28,
    'jimwlkAlphaS': 0,
    'jimwlkInitialX': 0.01,                        # W = 31.5 GeV (J/Psi, Q^2 = 0)
    'projectileX': 3.60813750e-06,      # W = 1632 GeV (J/Psi, Q^2 = 0)
    'targetX': 3.60813750e-06,          # W = 1632 GeV (J/Psi, Q^2 = 0)
    'jimwlkDs': 0.005,
    'jimwlkLambdaQCD': 0.040,
    'jimwlkMass': 0.4,
    'jimwlkSaveSnapshots': 1,
    'jimwlkXSnapshotList': [1.70844444e-03, 9.61000000e-04, 1.45392598e-05],  # W = 75, 100, 813 GeV (J/Psi, Q^2 = 0)
    'writeWilsonLines': 2,      # 2: binary
}

diffraction_dict = {
    'computeTotalCrossSection': 1,
    'analyzeDiffraction': 1,                # mode 1: JPsi
    'saveNucleusSnapshot': False,           # flag to save the trace of Wilson Line distribution
    "wavef_model": 'boostedgaussian',       # "gauslc"
    "wavef_file": 'gauss-boosted.dat',      # "gaus-lc.dat"
    "mcintpoints": 1000000,                  # "auto"
    "maxb": 20.,                            # GeV^-1
    "nbperp": 40,
    "ntheta": 32,
    # t values [GeV^2]: tlist if it is given, otherwise mint to maxt (inclusive) in steps of tstep
    "mint": 0.0,
    "maxt": 2.5,
    "tstep": 0.1,
    "tlist": [0.0, 0.001, 0.003, 0.005, 0.008, 0.01, 0.02, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5],
    "Q2List": [0.0,],
}
