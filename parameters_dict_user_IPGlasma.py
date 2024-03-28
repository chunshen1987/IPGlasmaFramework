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
    'OUTPUT_A_ONLY':0, 
    'Low_cut': 0,
    'High_cut': 1,
    'Q21': 0.0,
    'Q22': 0.0,
    'maxr': 2.0,
    'epslion': 0.1,
    'with_photon_kT': 0,  
    'run_jimwlk': 1, # flag to run the jimwlk
    'wavef_file': 1, # flag to run the jimwlk
    'saveNucleusSnapshot': False,       # flag to save the trace of Wilson Line distribution
}


# IPGlasma
ipglasma_dict = {
    'setWSDeformParams': 0,
    'DO_UPC_DIFF': 0,
    'R_WS': 6.81,
    'a_WS': 0.55,
    'beta2': 0.28,
    'beta3': 0.0,
    'beta4': 0.5,
    'gamma': 0.0,  
    'L': 8.,               # grid size in the transverse plane
    'size': 500,            # number of grid points of IP-Glasma computation
    'm': 0.4,
    'rmax': 1000.,
    'BG': 3.,
    'BGq': 0.3,
    'runTwoStage': 0,
    'WhichStage': 1,
    'force_dmin_flag': 1,
    'd_min': 0.9,
    'useConstituentQuarkProton': 3,   # 0: round proton; 3: fluctuating proton
    'runningCoupling': 0,
    'smearQs': 1,
    'smearingWidth': 0.6,
    'roots': 75.,
    'SigmaNN': 40.,
    'Rapidity': 0.03390454,
    'QsmuRatio': 0.7,
    'LOutput': 45,
    'bmin': 0.,
    'bmax': 0.,
    'Projectile': "p",
    'Target': "p",
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
    'readInitialWilsonLines': 0,
    'SubNucleonParamType': 0,
    'SubNucleonParamSet': 0,
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

# JIMWLK parameters
jimwlk_dict = {
    'mode': 1,
    'Nc': 3,
    'runningCoupling': 1,
    'size': 500,
    'steps': 115,
    'ds': 0.007,
    'measureSteps': 20,
    'initMethod': 11,
    'input_wline': "V-NN",
    'output_dir': "./",
    'R': 10.,
    'g2mua': 1.,
    'Lambda_QCD': 0.09,
    'kappa4Factor': 1,
    'g': 1.,
    'mjimwlk': 0.2,
    'L': 8.,
    'Ny': 100,
    'mu0': 0.28,
    'seed': 0, 
    'simpleLangevin': 1,
    'Fixedmu0Lambdaratio': 1,
    'Run_first_step': 1,
    'Output_V_files': 5,
    'measureSteps1': 25,
    'measureSteps2': 94,
    'measureSteps3': 114,
    'measureSteps4': 6000,
    'measureSteps5': 6000,
    'measureSteps6': 6000,
    'measureSteps7': 6000,
}


