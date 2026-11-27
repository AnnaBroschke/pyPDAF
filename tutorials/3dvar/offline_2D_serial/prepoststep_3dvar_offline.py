"""Pre- and post-step routine for parameterized 3D-Var
(translation of prepoststep_3dvar_offline.F90).

There is no ensemble in parameterized 3D-Var. The estimated error is computed
from the columns of B^1/2 (Vmat_p), and the state estimate is the single
column of ens_p.
"""
import numpy as np
import pyPDAF.PDAF

import mod_assimilation as assim

# Equivalent to the Fortran variable "LOGICAL, SAVE :: firsttime"
_firsttime = True


def _write_field(filename: str, vec: np.ndarray) -> None:
    """Write a state vector as 2D field (ny rows, nx columns)."""
    np.savetxt(filename, vec.reshape((assim.ny, assim.nx), order='F'))


def prepoststep_3dvar_offline(step: int, dim_p: int, dim_ens: int,
                              dim_ens_p: int, dim_obs_p: int,
                              state_p: np.ndarray, uinv: np.ndarray,
                              ens_p: np.ndarray, flag: int):
    """Analyse and write the 3D-Var state; return state_p, uinv, ens_p."""
    global _firsttime

    if _firsttime:
        print(' ' * 8 + 'Analyze forecasted state for 3D-Var')
    else:
        print(' ' * 8 + 'Analyze and write assimilated state for 3D-Var')

    # *** Standard deviation from the columns of B^1/2 ***
    # Vmat_p holds perturbations (mean zero), so do_mean=0 with a zero "mean"
    state_p[:] = 0.0
    _, ens_stddev, pdaf_status = pyPDAF.PDAF.diag_stddev_nompi(
        dim_p, assim.dim_cvec, state_p, assim.Vmat_p, 0)
    ens_stddev = ens_stddev * np.sqrt(assim.dim_cvec - 1)

    # The state estimate is stored in the single column of ens_p
    state_p[:] = ens_p[:, 0]

    print(' ' * 12 + f'RMS error according to modes Vmat_p: {ens_stddev:12.4E}')

    if not _firsttime:
        print(' ' * 8 + '--- write ensemble and state estimate')
        for member in range(dim_ens):
            _write_field(f'ens_{member + 1:02d}_ana.txt', ens_p[:, member])
        _write_field('state_ana.txt', state_p)

    _firsttime = False

    return state_p, uinv, ens_p
