"""Initialise PDAF (translation of init_pdaf_offline.F90).

Here the default settings for the assimilation are defined, the command
line is parsed and PDAF is initialised by PDAF3_init. During the
initialisation PDAF calls ``init_ens_offline`` to read the ensemble.
"""
import numpy as np
import pyPDAF.PDAF
import pyPDAF.PDAF3
import pyPDAF.PDAFomi

import mod_assimilation as assim
import mod_parallel_pdaf as par
import obs_A_pdafomi as obs_A
import obs_B_pdafomi as obs_B
import obs_C_pdafomi as obs_C
from init_ens_offline import init_ens_offline
from init_pdaf_info import init_pdaf_info
from init_pdaf_parse import init_pdaf_parse

# Number of observation types handled by PDAFomi (A, B, C)
N_OBS_TYPES = 3


def init_pdaf() -> None:
    """Set defaults, parse command line and call PDAF3_init."""
    if par.mype_world == 0:
        print('\n INITIALIZE PDAF - OFFLINE MODE')

    # *** Settings for PDAF (defaults, can be changed by command line) ***
    assim.screen = 2       # Screen output: (1) regular, (2) add timings
    assim.dim_ens = 9      # Size of ensemble
    assim.filtertype = 6   # Type of filter (6 = ESTKF, 7 = LESTKF, ...)
    assim.subtype = 0      # Subtype of filter
    assim.forget = 1.0     # Forgetting factor
    assim.type_forget = 0  # Type of forgetting factor (0: fixed)
    assim.type_trans = 0   # Type of ensemble transformation (0: deterministic)
    assim.type_sqrt = 0    # Type of transform matrix square-root

    # *** Which observations to assimilate ***
    obs_A.assim_A = True
    obs_B.assim_B = False
    obs_C.assim_C = False

    # *** Observation error standard deviations ***
    obs_A.rms_obs_A = 0.5
    obs_B.rms_obs_B = 0.5
    obs_C.rms_obs_C = 0.5

    # *** Localisation settings ***
    assim.locweight = 0           # Type of localizing weighting
    assim.cradius = 0.0           # Cut-off radius in grid points
    assim.sradius = assim.cradius # Support radius for 5th-order polynomial

    # *** Parse command line options ***
    init_pdaf_parse()

    if par.mype_world == 0:
        init_pdaf_info()

    # *** Initialize PDAF ***
    # pyPDAF expects numpy arrays with the correct C types
    filter_param_i = np.array([assim.dim_state_p, assim.dim_ens], dtype=np.intc)
    filter_param_r = np.array([assim.forget], dtype=np.float64)

    _, _, status_pdaf = pyPDAF.PDAF3.init(assim.filtertype, assim.subtype, 0,
                                          filter_param_i, len(filter_param_i),
                                          filter_param_r, len(filter_param_r),
                                          init_ens_offline, assim.screen)

    # Additional parameters for PDAF
    status_pdaf = pyPDAF.PDAF.set_iparam(5, assim.type_forget, status_pdaf)
    status_pdaf = pyPDAF.PDAF.set_iparam(6, assim.type_trans, status_pdaf)
    status_pdaf = pyPDAF.PDAF.set_iparam(8, assim.observe_ens, status_pdaf)
    status_pdaf = pyPDAF.PDAF.set_iparam(9, assim.type_obs_init, status_pdaf)

    if status_pdaf != 0:
        print(f'\n ERROR {status_pdaf:3d} in initialization of PDAF '
              f'- stopping! (PE {par.mype_world:4d})')
        pyPDAF.PDAF.abort(1)

    # *** pyPDAF-specific: allocate the PDAFomi observation types ***
    # In Fortran each obs module holds its own ``TYPE(obs_f) :: thisobs``.
    # In pyPDAF these objects live inside the library and are addressed
    # by an index i_obs = 1, ..., N_OBS_TYPES.
    pyPDAF.PDAFomi.init(N_OBS_TYPES)
