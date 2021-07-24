#!/usr/bin/env python3
"""
    This script contains all the user modified parameters in
    the IPGlasmaFramework package.
"""

# control parameters
control_dict = {
    'initial_state_type': "IPGlasma",
    'walltime': "10:00:00",  # walltime to run
    'save_ipglasma_results': True,
}


# IPGlasma
ipglasma_dict = {
    'bmin': 0.,
    'bmax': 20.,
    'Projectile': "Au",
    'Target': "Au",
    'roots': 200.,
    'SigmaNN': 42.,
    'useConstituentQuarkProton': 3,   # 0: round proton; 3: fluctuating proton
}

