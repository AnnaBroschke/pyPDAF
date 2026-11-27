"""Initialise PDAF for 3D-Var (translation of 3dvar/online_2D_serialmodel/init_pdaf.F90).

filtertype 200 selects the 3D-Var methods; the variant is chosen by subtype:

* 0: parameterized 3D-Var (run with 1 process, -dim_ens 1 -dim_cvec 9)
* 1: 3D-EnVar, ensemble transformation with LESTKF
* 2: 3D-EnVar, ensemble transformation with ESTKF
* 3: hybrid 3D-Var, ensemble transformation with LESTKF
* 4: hybrid 3D-Var, ensemble transformation with ESTKF
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
from init_3dvar_pdaf import init_3dvar_pdaf
from init_ens_pdaf import init_ens_pdaf
from init_pdaf_parse import init_pdaf_parse
from next_observation_pdaf import next_observation_pdaf
from prepoststep_3dvar_pdaf import prepoststep_3dvar_pdaf
from prepoststep_ens_pdaf import prepoststep_ens_pdaf

# Number of observation types handled by PDAFomi (A, B, C)
N_OBS_TYPES = 3


def init_pdaf() -> None:
    """Set defaults, parse command line and initialise PDAF."""
    if par.mype_world == 0:
        print('\n INITIALIZE PDAF - ONLINE MODE')

    # State dimension
    assim.dim_state_p = model.nx * model.ny

    # *** Settings for PDAF (defaults, can be changed by command line) ***
    assim.screen = 2                 # Screen output
    assim.dim_ens = par.n_modeltasks # Size of ensemble = number of model tasks
    assim.dim_cvec = assim.dim_ens   # Size of control vector (parameterized part)
    assim.mcols_cvec_ens = 1         # Factor for columns of ensemble B^1/2
    assim.filtertype = 200           # 3D-Var methods
    assim.subtype = 0                # 0: parameterized 3D-Var (see module docstring)
    assim.forget = 1.0               # Forgetting factor (for the ensemble methods)
    assim.type_opt = 1               # Optimizer: (1) LBFGS, (2) CG+, (3) plain CG
    assim.beta_3dvar = 0.5           # Hybrid weight for hybrid 3D-Var
    assim.ensgroup = 1               # Read ens_X.txt

    # *** Assimilation interval ***
    assim.delt_obs = 2

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

    # Size of the ensemble part of the control vector
    assim.dim_cvec_ens = assim.dim_ens * assim.mcols_cvec_ens

    # *** Initialize PDAF ***
    filter_param_i = np.array([assim.dim_state_p, assim.dim_ens, assim.type_opt,
                               assim.dim_cvec, assim.dim_cvec_ens], dtype=np.intc)
    filter_param_r = np.array([assim.forget, assim.beta_3dvar], dtype=np.float64)

    if assim.subtype == 0:
        _, _, status_pdaf = pyPDAF.PDAF3.init(assim.filtertype, assim.subtype, 0,
                                              filter_param_i, 5,
                                              filter_param_r, 1,
                                              init_3dvar_pdaf, assim.screen)
    else:
        _, _, status_pdaf = pyPDAF.PDAF3.init(assim.filtertype, assim.subtype, 0,
                                              filter_param_i, 5,
                                              filter_param_r, 2,
                                              init_ens_pdaf, assim.screen)

    if status_pdaf != 0:
        print(f'\n ERROR {status_pdaf:3d} in initialization of PDAF '
              f'- stopping! (PE {par.mype_world:4d})')
        pyPDAF.PDAF.abort(1)

    # *** pyPDAF-specific: allocate the PDAFomi observation types ***
    pyPDAF.PDAFomi.init(N_OBS_TYPES)

    # *** Prepare forecasts: distribute the initial state/ensemble ***
    if not (assim.filtertype == 200 and assim.subtype == 0):
        status_pdaf = pyPDAF.PDAF3.init_forecast(next_observation_pdaf,
                                                 distribute_state_pdaf,
                                                 prepoststep_ens_pdaf, status_pdaf)
    else:
        status_pdaf = pyPDAF.PDAF3.init_forecast(next_observation_pdaf,
                                                 distribute_state_pdaf,
                                                 prepoststep_3dvar_pdaf, status_pdaf)
