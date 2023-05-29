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
    'analyzeDiffraction': 3,            # 1: JPsi only; 2: JPsi + rho
    'Low_cut': 0.712599089222466,                     # The low cut for the Q^2 integral
    'High_cut': 2.0,                    # The upper cut for the Q^2 integral
    'Q21': 0.0,                         # the Q^2 for the rho production
    'Q22': 30.,                         # the Q^2 for the rho production
    'saveNucleusSnapshot': False,       # flag to save the trace of Wilson Line distributioni
    'maxr': 1.0,                        # the maxr for the rho production
    'OUTPUT_A_ONLY': 1,                    # Output the b and theta_b 2-d table of A
    'epslion': 0.1,
    'with_photon_kT': 0,                        # the maxr for the rho production
}


# IPGlasma
ipglasma_dict = {
    'setWSDeformParams': 1,
    'R_WS': 6.9,
    'a_WS': 0.535,
    'beta2': -0.13,
    'force_dmin_flag': 0,
    'd_min': 0.9,
    'beta3': 0.0,
    'beta4': -0.03,
    'gamma': 0.0,  
    'L': 30.,               # grid size in the transverse plane
    'size': 1024,            # number of grid points of IP-Glasma computation
    'm': 0.2573,
    'rmax': 1000.,
    'BG': 4.3674,
    'BGq': 0.3353,
    'DO_UPC_DIFF': 1,
    'DO_SOFT_RAD': 0, 
    'useConstituentQuarkProton': 3.,   # 0: round proton; 3: fluctuating proton
    'runningCoupling': 0,
    'smearQs': 1,
    'smearingWidth': 0.5950,
    'roots': 75.,
    'SigmaNN': 40.,
    'Rapidity': 0.0,
    'QsmuRatio': 0.6661,
    'dqMin': 0.2582,
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

