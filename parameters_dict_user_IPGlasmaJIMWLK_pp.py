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
    'rmax': 1000.,
    'BG': 3.,
    'BGq': 0.3,
    'omega': 1.0,
    'useConstituentQuarkProton': 3,   # 0: round proton; 3: fluctuating proton
    'smearingWidth': 0.6,
    'QsmuRatio': 0.7,
    'useFluctuatingx': 0,
    'roots': 200.,
    'SigmaNN': 42.,
    'Rapidity': 0.,
    'Projectile': "p",
    'Target': "p",
    'useTimeForSeed': 1,
    'useJIMWLK': 1,
    'mu0_jimwlk': 0.28,
    'simpleLangevin': 1,
    'alphas_jimwlk': 0,
    'jimwlk_ic_x': 0.01,                        # W = 31.5 GeV (J/Psi, Q^2 = 0)
    'x_projectile_jimwlk': 3.60813750e-06,      # W = 1632 GeV (J/Psi, Q^2 = 0)
    'x_target_jimwlk': 3.60813750e-06,          # W = 1632 GeV (J/Psi, Q^2 = 0)
    'Ds_jimwlk': 0.005,
    'Lambda_QCD_jimwlk': 0.040,
    'm_jimwlk': 0.4,
    'saveSnapshots': 1,
    'xSnapshotList': [1.70844444e-03, 9.61000000e-04, 1.45392598e-05],  # W = 75, 100, 813 GeV (J/Psi, Q^2 = 0)
    'writeWilsonLines': 2,      # 2: binary
}

diffraction_dict = {
    'computeTotalCrossSection': 1,
    'analyzeDiffraction': 1,                # mode 1: JPsi
    'saveNucleusSnapshot': False,           # flag to save the trace of Wilson Line distribution
    "wavef_model": 'boostedgaussian',       # "gauslc"
    "wavef_file": 'gauss-boosted.dat',      # "gaus-lc.dat"
    "mcintpoints": 100000,                  # "auto"
    "mint": 0.0,
    "maxt": 2.5,
    "tstep": 0.1,
    "Q2List": [0.0,],
}
