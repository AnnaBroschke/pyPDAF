"""Initialise PDAF for 3D-Var with a parallelized model
(translation of 3dvar/online_2D_parallelmodel/init_pdaf.F90).

For the parallelized optimizers (type_opt 12: CG+, 13: plain CG) the control
vector is distributed over the processes of a model task (= filter
processes). Its local sizes and offsets are computed here; the local sizes
are passed to PDAF.
"""
import numpy as np
import pyPDAF.PDAF
import pyPDAF.PDAF3
import pyPDAF.PDAFomi

import mod_assimilation as assim
import mod_model as model
import mod_parallel_model as pm
import mod_parallel_pdaf as par
import obs_A_pdafomi as obs_A
import obs_B_pdafomi as obs_B
from distribute_state_pdaf import distribute_state_pdaf
from init_3dvar_pdaf import init_3dvar_pdaf
from init_ens_pdaf import init_ens_pdaf
from init_pdaf_parse import init_pdaf_parse
from next_observation_pdaf import next_observation_pdaf
from prepoststep_3dvar_pdaf import prepoststep_3dvar_pdaf
from prepoststep_ens_pdaf import prepoststep_ens_pdaf

# Number of observation types handled by PDAFomi (A, B)
N_OBS_TYPES = 2


def _decompose(dim: int, npes: int, name: str) -> tuple[np.ndarray, np.ndarray]:
    """Split a vector of length dim into npes parts (sizes and offsets)."""
    dims = np.full(npes, dim // npes, dtype=int)
    dims[:dim - npes * dims[0]] += 1
    off = np.concatenate(([0], np.cumsum(dims)[:-1])).astype(int)
    if pm.mype_world == 0:
        print('\n' + ' ' * 2 + f'-- Decomposition of control vector over{npes:3d} PEs')
        for i in range(npes):
            print(' ' * 5 + f'task {par.task_id:3d} PE(model) {i:3d} '
                  f'{name}: {dims[i]:5d}{off[i]:5d}')
    return dims, off


def init_pdaf() -> None:
    """Set defaults, parse command line and initialise PDAF."""
    if pm.mype_world == 0:
        print('\n INITIALIZE PDAF - ONLINE MODE')

    assim.dim_state_p = model.nx_p * model.ny
    assim.dim_state = model.nx * model.ny

    # *** Settings for PDAF (defaults, can be changed by command line) ***
    assim.screen = 2
    assim.dim_ens = par.n_modeltasks
    assim.dim_cvec = assim.dim_ens
    assim.mcols_cvec_ens = 1
    assim.filtertype = 200
    assim.subtype = 0
    assim.forget = 1.0
    assim.type_opt = 1
    assim.beta_3dvar = 0.5
    assim.delt_obs = 2

    obs_A.assim_A = True
    obs_B.assim_B = False
    obs_A.rms_obs_A = 0.5
    obs_B.rms_obs_B = 0.5

    assim.locweight = 0
    assim.cradius = 0.0
    assim.sradius = assim.cradius

    init_pdaf_parse()

    assim.dim_cvec_ens = assim.dim_ens * assim.mcols_cvec_ens
    parallel_opt = assim.type_opt in (12, 13)

    # *** Decomposition of the ensemble part of the control vector ***
    if assim.filtertype == 200 and assim.subtype > 0 and parallel_opt:
        assim.dims_cv_ens_p, assim.off_cv_ens_p = _decompose(
            assim.dim_cvec_ens, pm.npes_2Dmodel, 'dims_cv_ens_p, off_cv_ens_p')
        dim_cvec_ens_p = int(assim.dims_cv_ens_p[pm.mype_2Dmodel])
    else:
        dim_cvec_ens_p = assim.dim_cvec_ens

    # *** Decomposition of the parameterized part of the control vector ***
    if assim.filtertype == 200 and assim.subtype in (0, 3, 4) and parallel_opt:
        assim.dims_cv_p, assim.off_cv_p = _decompose(
            assim.dim_cvec, pm.npes_2Dmodel, 'dims_cv_p, off_cv_p')
        dim_cvec_p = int(assim.dims_cv_p[pm.mype_2Dmodel])
    else:
        dim_cvec_p = assim.dim_cvec

    # *** Initialize PDAF ***
    filter_param_i = np.array([assim.dim_state_p, assim.dim_ens, assim.type_opt,
                               dim_cvec_p, dim_cvec_ens_p], dtype=np.intc)
    filter_param_r = np.array([assim.forget, assim.beta_3dvar], dtype=np.float64)

    if assim.subtype == 0:
        _, _, status_pdaf = pyPDAF.PDAF3.init(assim.filtertype, assim.subtype, 0,
                                              filter_param_i, 5, filter_param_r, 1,
                                              init_3dvar_pdaf, assim.screen)
    else:
        _, _, status_pdaf = pyPDAF.PDAF3.init(assim.filtertype, assim.subtype, 0,
                                              filter_param_i, 5, filter_param_r, 2,
                                              init_ens_pdaf, assim.screen)

    if status_pdaf != 0:
        print(f'\n ERROR {status_pdaf:3d} in initialization of PDAF '
              f'- stopping! (PE {pm.mype_world:4d})')
        pyPDAF.PDAF.abort(1)

    pyPDAF.PDAFomi.init(N_OBS_TYPES)

    if not (assim.filtertype == 200 and assim.subtype == 0):
        status_pdaf = pyPDAF.PDAF3.init_forecast(next_observation_pdaf,
                                                 distribute_state_pdaf,
                                                 prepoststep_ens_pdaf, status_pdaf)
    else:
        status_pdaf = pyPDAF.PDAF3.init_forecast(next_observation_pdaf,
                                                 distribute_state_pdaf,
                                                 prepoststep_3dvar_pdaf, status_pdaf)
