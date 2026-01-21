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
    'L': 18.,           # grid size in the transverse plane
    'size': 720,        # number of grid points of IP-Glasma computation
    'LOutput': 18.,
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
    'Projectile': "Pb",
    'Target': "Pb",
    'useTimeForSeed': 1,
    'useJIMWLK': 1,
    'mu0_jimwlk': 0.28,
    'simpleLangevin': 1,
    'alphas_jimwlk': 0,
    'jimwlk_ic_x': 0.01,                        # W = 31 GeV (J/Psi, Q^2 = 0)
    'x_projectile_jimwlk': 1.45374716e-05,      # W = 813.05 GeV (J/Psi, Q^2 = 0)
    'x_target_jimwlk': 1.45374716e-05,          # W = 813.05 GeV (J/Psi, Q^2 = 0)
    'Ds_jimwlk': 0.005,
    'Lambda_QCD_jimwlk': 0.040,
    'm_jimwlk': 0.4,
    'saveSnapshots': 1,
    'xSnapshotList': [4.56139851e-03, 6.18101984e-04, 6.51719835e-05],  # W = 45.9, 124.69, 384 GeV (J/Psi, Q^2 = 0)
    'writeWilsonLines': 2,      # 2: binary
}

diffraction_dict = {
    'computeTotalCrossSection': 1,
    'analyzeDiffraction': 0,                # mode 1: JPsi
    'saveNucleusSnapshot': False,           # flag to save the trace of Wilson Line distribution
    "wavef_model": 'boostedgaussian',       # "gauslc"
    "wavef_file": 'gauss-boosted.dat',      # "gaus-lc.dat"
    "mcintpoints": 4000000,                  # "auto"
    "maxb": 51.,                            # GeV^-1
    "nbperp": 50,
    "ntheta": 64,
    "mint": 0.0,
    "maxt": 1.0,
    "tstep": 0.1,
    "tlist": [0.0, 0.001, 0.003, 0.005, 0.008, 0.01, 0.02, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5],
    "Q2List": [0.0,],
}
