"""Initialise PDAF (translation of init_pdaf.F90).

Defines the default settings, parses the command line, calls PDAF3_init
(which calls init_ens_pdaf) and PDAF_init_forecast (which distributes the
ensemble to the model tasks via distribute_state_pdaf).
"""
import numpy as np
import pyPDAF.PDAF
import pyPDAF.PDAF3
import pyPDAF.PDAFomi

import mod_assimilation as assim
import mod_model as model
import mod_parallel_pdaf as par
import obs_A_pdafomi as obs_A
import obs_B_pdafomi as obs_B
import obs_C_pdafomi as obs_C
from distribute_state_pdaf import distribute_state_pdaf
from init_ens_pdaf import init_ens_pdaf
from init_pdaf_info import init_pdaf_info
from init_pdaf_parse import init_pdaf_parse
from next_observation_pdaf import next_observation_pdaf
from prepoststep_pdaf import prepoststep_pdaf

# Number of observation types handled by PDAFomi (A, B, C)
N_OBS_TYPES = 3


def init_pdaf() -> None:
    """Set defaults, parse command line and initialise PDAF."""
    if par.mype_world == 0:
        print('\n INITIALIZE PDAF - ONLINE MODE')

    # State dimension
    assim.dim_state_p = model.nx * model.ny

    # *** Settings for PDAF (defaults, can be changed by command line) ***
    assim.screen = 2                 # Screen output: (1) regular, (2) add timings
    assim.dim_ens = par.n_modeltasks # Size of ensemble = number of model tasks
    assim.filtertype = 6             # Type of filter (6 = ESTKF, 7 = LESTKF, ...)
    assim.subtype = 0                # Subtype of filter
    assim.forget = 1.0               # Forgetting factor
    assim.type_forget = 0            # Type of forgetting factor
    assim.type_trans = 0             # Type of ensemble transformation
    assim.type_sqrt = 0              # Type of transform matrix square-root
    assim.ensgroup = 1               # Which ensemble to read (1: ens_X, 2: ensB_X)

    # *** Assimilation interval ***
    assim.delt_obs = 2               # Time steps between analysis steps

    # *** Which observations to assimilate ***
    obs_A.assim_A = True
    obs_B.assim_B = False
    obs_C.assim_C = False

    # *** Observation error standard deviations ***
    obs_A.rms_obs_A = 0.5
    obs_B.rms_obs_B = 0.5
    obs_C.rms_obs_C = 0.5

    # *** Localisation settings ***
    assim.locweight = 0
    assim.cradius = 0.0
    assim.sradius = assim.cradius

    # *** Parse command line options ***
    init_pdaf_parse()

    if par.mype_world == 0:
        init_pdaf_info()

    # *** Initialize PDAF ***
    filter_param_i = np.array([assim.dim_state_p, assim.dim_ens], dtype=np.intc)
    filter_param_r = np.array([assim.forget], dtype=np.float64)

    _, _, status_pdaf = pyPDAF.PDAF3.init(assim.filtertype, assim.subtype, 0,
                                          filter_param_i, len(filter_param_i),
                                          filter_param_r, len(filter_param_r),
                                          init_ens_pdaf, assim.screen)

    status_pdaf = pyPDAF.PDAF.set_iparam(5, assim.type_forget, status_pdaf)
    status_pdaf = pyPDAF.PDAF.set_iparam(6, assim.type_trans, status_pdaf)
    status_pdaf = pyPDAF.PDAF.set_iparam(7, assim.type_sqrt, status_pdaf)
    status_pdaf = pyPDAF.PDAF.set_iparam(8, assim.observe_ens, status_pdaf)
    status_pdaf = pyPDAF.PDAF.set_iparam(9, assim.type_obs_init, status_pdaf)

    if status_pdaf != 0:
        print(f'\n ERROR {status_pdaf:3d} in initialization of PDAF '
              f'- stopping! (PE {par.mype_world:4d})')
        pyPDAF.PDAF.abort(1)

    # *** pyPDAF-specific: allocate the PDAFomi observation types ***
    pyPDAF.PDAFomi.init(N_OBS_TYPES)

    # *** Prepare ensemble forecasts: distribute the initial ensemble ***
    status_pdaf = pyPDAF.PDAF3.init_forecast(next_observation_pdaf,
                                             distribute_state_pdaf,
                                             prepoststep_pdaf, status_pdaf)
