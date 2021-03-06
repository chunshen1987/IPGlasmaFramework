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
    'analyzeDiffraction': 1,            # 1: JPsi only; 2: JPsi + rho
    'saveNucleusSnapshot': False,       # flag to save the trace of Wilson Line distribution
}


# IPGlasma
ipglasma_dict = {
    'L': 5.12,               # grid size in the transverse plane
    'size': 1024,            # number of grid points of IP-Glasma computation
    'm': 0.4,
    'rmax': 1000.,
    'BG': 3.,
    'BGq': 0.3,
    'useConstituentQuarkProton': 3,   # 0: round proton; 3: fluctuating proton
    'shiftConstituentQuarkProtonOrigin': 1,
    'smearQs': 1,
    'smearingWidth': 0.6,
    'roots': 75.,
    'SigmaNN': 40.,
    'Rapidity': 1.7689,
    'QsmuRatio': 0.7,
    'bmin': 0.,
    'bmax': 0.,
    'Projectile': "p",
    'Target': "p",
    'maxtime': 0.0,
    'useTimeForSeed': 1,
    'LOutput': 5.12,
    'sizeOutput': 1024,
    'writeOutputs': 0,
    'writeInitialWilsonLines': 2,
}

