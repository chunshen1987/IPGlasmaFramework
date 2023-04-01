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
    'analyzeDiffraction': 2,            # 1: JPsi only; 2: JPsi + rho
    'Low_cut': 0.8,                     # The low cut for the Q^2 integral
    'High_cut': 1.2,                    # The upper cut for the Q^2 integral
    'saveNucleusSnapshot': False,       # flag to save the trace of Wilson Line distribution
}


# IPGlasma
ipglasma_dict = {
    'setWSDeformParams': 0,
    'R_WS': 6.37,
    'a_WS': 0.535,
    'beta2': 0.0,
    'beta3': 0.0,
    'beta4': 0.00,
    'gamma': 0.0,  
    'DO_UPC_DIFF': 1,
    'L': 30.,               # grid size in the transverse plane
    'size': 1024,            # number of grid points of IP-Glasma computation
    'm': 0.4,
    'rmax': 1000.,
    'BG': 3.,
    'BGq': 0.3,
    'useConstituentQuarkProton': 3,   # 0: round proton; 3: fluctuating proton
    'runningCoupling': 0,
    'smearQs': 1,
    'smearingWidth': 0.6,
    'roots': 75.,
    'SigmaNN': 40.,
    'Rapidity': 0.0,
    'QsmuRatio': 0.7,
    'LOutput': 45,
    'bmin': 0.,
    'bmax': 0.,
    'Projectile': "Au",
    'Target': "Au",
    'maxtime': 0.0,
    'useTimeForSeed': 1,
    'sizeOutput': 1024,
    'writeOutputs': 0,
    'writeInitialWilsonLines': 2,
    'useFluctuatingx': 0,
    'minimumQs2ST': 0,
    'readMultFromFile': 0,
    'Nc': 3,
    'UVdamp': 0.,
    'Jacobianm': 0.35,
    'g': 1.,
    'useSmoothNucleus': 0,
    'shiftConstituentQuarkProtonOrigin': 1,
    'muZero': 0.3,
    'c': 0.2,
    'g2mu': 0.1,
    'useFatTails': 0,
    'tDistNu': 3,
    'protonAnisotropy': 0,
    'usePseudoRapidity': 0,
    'xFromThisFactorTimesQs': 1,
    'useNucleus': 1,
    'useGaussian': 0,
    'nucleonPositionsFromFile': 0,
#    'NucleusQsTableFileName': qs2Adj_vs_Tp_vs_Y_200.in,
    'samplebFromLinearDistribution': 1,
    'runWith0Min1Avg2MaxQs': 2,
    'runWithThisFactorTimesQs': 0.5,
    'runWithLocalQs': 0,
    'runWithkt': 0,
    'Ny': 50,
    'useSeedList': 0,
    'seed': 0,
    'lightNucleusOption': 2,
    'beta2': 0.28,
    'useFixedNpart': 0,
    'averageOverThisManyNuclei': 1,
    'gaussianWounding': 1,
    'inverseQsForMaxTime': 0,
    'dtau': 0.1,
    'detaOutput': 0,
    'writeEvolution': 0,
    'etaSizeOutput': 1,
    'writeOutputsToHDF5': 0,
    'mode': 1,
    'readMultFromFile': 0,
#    'EndOfFile',
}

