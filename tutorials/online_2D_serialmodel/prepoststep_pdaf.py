"""Pre- and post-step routine (translation of prepoststep_pdaf.F90).

Called by PDAF at the initial time, before each analysis (forecast, step<0)
and after each analysis (step>0). Computes the ensemble spread and writes
``ens_XX_stepYY_{for,ana}.txt`` and ``state_stepYY_{for,ana}.txt``.
"""
import numpy as np
import pyPDAF.PDAF

import mod_model as model
import mod_parallel_pdaf as par

# Equivalent to the Fortran variable "LOGICAL, SAVE :: firsttime"
_firsttime = True


def _write_field(filename: str, vec: np.ndarray) -> None:
    """Write a state vector as 2D field (ny rows, nx columns)."""
    np.savetxt(filename, vec.reshape((model.ny, model.nx), order='F'))


def prepoststep_pdaf(step: int, dim_p: int, dim_ens: int, dim_ens_p: int,
                     dim_obs_p: int, state_p: np.ndarray, uinv: np.ndarray,
                     ens_p: np.ndarray, flag: int):
    """Analyse and write the ensemble; return state_p, uinv, ens_p."""
    global _firsttime

    if _firsttime:
        anastr = 'ini'
        msg = 'Analyze initial state ensemble'
    elif step < 0:
        anastr = 'for'
        msg = 'Analyze and write forecasted state ensemble'
    else:
        anastr = 'ana'
        msg = 'Analyze and write assimilated state ensemble'
    if par.mype_filter == 0:
        print(' ' * 8 + msg)

    # *** Ensemble mean (do_mean=1) and ensemble standard deviation ***
    state_p, ens_stddev, pdaf_status = pyPDAF.PDAF.diag_stddev(
        dim_p, dim_ens, state_p, ens_p, 1, par.COMM_filter)

    if par.mype_filter == 0:
        print(' ' * 12 + 'RMS error according to sampled variance: '
              f'{ens_stddev:12.4E}')

    # *** Write ensemble and state estimate (not at initial time) ***
    if not _firsttime:
        print(' ' * 8 + '--- write ensemble and state estimate')
        stepstr = f'{abs(step):02d}'
        for member in range(dim_ens):
            _write_field(f'ens_{member + 1:02d}_step{stepstr}_{anastr}.txt',
                         ens_p[:, member])
        _write_field(f'state_step{stepstr}_{anastr}.txt', state_p)

    _firsttime = False

    return state_p, uinv, ens_p
