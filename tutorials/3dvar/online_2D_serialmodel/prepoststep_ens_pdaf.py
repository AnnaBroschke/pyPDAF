"""Pre- and post-step routine for ensemble/hybrid 3D-Var
(translation of 3dvar/online_2D_serialmodel/prepoststep_ens_pdaf.F90).

Same as prepoststep_pdaf of online_2D_serialmodel, but uses
PDAF_diag_stddev_nompi.
"""
import numpy as np
import pyPDAF.PDAF

import mod_model as model

# Equivalent to the Fortran variable "LOGICAL, SAVE :: firsttime"
_firsttime = True


def _write_field(filename: str, vec: np.ndarray) -> None:
    """Write a state vector as 2D field (ny rows, nx columns)."""
    np.savetxt(filename, vec.reshape((model.ny, model.nx), order='F'))


def prepoststep_ens_pdaf(step: int, dim_p: int, dim_ens: int, dim_ens_p: int,
                         dim_obs_p: int, state_p: np.ndarray, uinv: np.ndarray,
                         ens_p: np.ndarray, flag: int):
    """Analyse and write the ensemble; return state_p, uinv, ens_p."""
    global _firsttime

    if _firsttime:
        anastr = 'ini'
        print(' ' * 8 + 'Analyze initial state ensemble')
    elif step < 0:
        anastr = 'for'
        print(' ' * 8 + 'Analyze and write forecasted state ensemble')
    else:
        anastr = 'ana'
        print(' ' * 8 + 'Analyze and write assimilated state ensemble')

    state_p, ens_stddev, pdaf_status = pyPDAF.PDAF.diag_stddev_nompi(
        dim_p, dim_ens, state_p, ens_p, 1)

    print(' ' * 12 + f'RMS error according to sampled variance: {ens_stddev:12.4E}')

    if not _firsttime:
        print(' ' * 8 + '--- write ensemble and state estimate')
        stepstr = f'{abs(step):02d}'
        for member in range(dim_ens):
            _write_field(f'ens_{member + 1:02d}_step{stepstr}_{anastr}.txt',
                         ens_p[:, member])
        _write_field(f'state_step{stepstr}_{anastr}.txt', state_p)

    _firsttime = False

    return state_p, uinv, ens_p
