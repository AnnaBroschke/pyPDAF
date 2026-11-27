"""Pre- and post-step routine for ensemble/hybrid 3D-Var
(translation of 3dvar/offline_2D_serial/prepoststep_ens_offline.F90).

Same as in offline_2D_serial, but uses PDAF_diag_stddev_nompi.
"""
import numpy as np
import pyPDAF.PDAF

import mod_assimilation as assim

# Equivalent to the Fortran variable "LOGICAL, SAVE :: firsttime"
_firsttime = True


def _write_field(filename: str, vec: np.ndarray) -> None:
    """Write a state vector as 2D field (ny rows, nx columns)."""
    np.savetxt(filename, vec.reshape((assim.ny, assim.nx), order='F'))


def prepoststep_ens_offline(step: int, dim_p: int, dim_ens: int,
                            dim_ens_p: int, dim_obs_p: int,
                            state_p: np.ndarray, uinv: np.ndarray,
                            ens_p: np.ndarray, flag: int):
    """Analyse and write the ensemble; return state_p, uinv, ens_p."""
    global _firsttime

    if _firsttime:
        print(' ' * 8 + 'Analyze forecasted state ensemble')
    else:
        print(' ' * 8 + 'Analyze and write assimilated state ensemble')

    # *** Ensemble mean (do_mean=1) and standard deviation ***
    state_p, ens_stddev, pdaf_status = pyPDAF.PDAF.diag_stddev_nompi(
        dim_p, dim_ens, state_p, ens_p, 1)

    print(' ' * 12 + f'RMS error according to sampled variance: {ens_stddev:12.4E}')

    if not _firsttime:
        print(' ' * 8 + '--- write ensemble and state estimate')
        for member in range(dim_ens):
            _write_field(f'ens_{member + 1:02d}_ana.txt', ens_p[:, member])
        _write_field('state_ana.txt', state_p)

    _firsttime = False

    return state_p, uinv, ens_p
