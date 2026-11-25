"""Pre- and post-step routine (translation of prepoststep_ens_offline.F90).

Call-back routine that is called by PDAF before the analysis (forecast
ensemble) and after the analysis (analysis ensemble). Here we compute the
ensemble spread and write the analysis ensemble and state to files.
"""
import numpy as np
import pyPDAF.PDAF

import mod_model_pdaf as model
import mod_parallel_pdaf as par

# Equivalent to the Fortran variable "LOGICAL, SAVE :: firsttime"
_firsttime = True


def _write_field(filename: str, vec: np.ndarray) -> None:
    """Write a state vector as 2D field (ny rows, nx columns)."""
    field = vec.reshape((model.ny, model.nx), order='F')
    np.savetxt(filename, field)


def prepoststep_ens_offline(step: int, dim_p: int, dim_ens: int,
                            dim_ens_p: int, dim_obs_p: int,
                            state_p: np.ndarray, uinv: np.ndarray,
                            ens_p: np.ndarray, flag: int):
    """Analyse and write the ensemble.

    Returns the (possibly modified) arrays state_p, uinv, ens_p to PDAF.
    """
    global _firsttime

    if par.mype_filter == 0:
        if _firsttime:
            print(' ' * 8 + 'Analyze forecasted state ensemble')
        else:
            print(' ' * 8 + 'Analyze and write assimilated state ensemble')

    # *** Compute ensemble mean (do_mean=1) and ensemble standard deviation ***
    state_p, ens_stddev, pdaf_status = pyPDAF.PDAF.diag_stddev(
        dim_p, dim_ens, state_p, ens_p, 1, par.COMM_filter)

    if par.mype_filter == 0:
        print(' ' * 12 + 'RMS error according to sampled standard deviation: '
              f'{ens_stddev:12.4E}')

    # *** Write analysis ensemble and state estimate ***
    if not _firsttime:
        print(' ' * 8 + '--- write ensemble and state estimate')
        for member in range(dim_ens):
            _write_field(f'ens_{member + 1:02d}_ana.txt', ens_p[:, member])
        _write_field('state_ana.txt', state_p)

    _firsttime = False

    return state_p, uinv, ens_p
