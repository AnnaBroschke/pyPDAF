"""Pre- and post-step routine (translation of prepoststep_pdaf.F90).

Computes the ensemble standard deviation separately for each field and
writes ``ens{A,B}_XX_stepYY_{for,ana}.txt`` and
``state{A,B}_stepYY_{for,ana}.txt``.
"""
import numpy as np
import pyPDAF.PDAF

import mod_model as model
import mod_parallel_pdaf as par
import mod_statevector_pdaf as sv

# Equivalent to the Fortran variable "LOGICAL, SAVE :: firsttime"
_firsttime = True


def _write_field(filename: str, vec: np.ndarray) -> None:
    """Write one field of the state vector as 2D field (ny rows, nx columns)."""
    np.savetxt(filename, vec.reshape((model.ny, model.nx), order='F'))


def prepoststep_pdaf(step: int, dim_p: int, dim_ens: int, dim_ens_p: int,
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

    # *** Ensemble mean and standard deviation for each field ***
    # PDAF_diag_stddev is called with the part of state and ensemble that
    # belongs to the field. The ensemble mean is written into that part of
    # state_p (do_mean=1).
    ens_stddev = np.zeros(sv.n_fields)
    for j, f in enumerate(sv.sfields):
        state_f, ens_stddev[j], pdaf_status = pyPDAF.PDAF.diag_stddev(
            f.dim, dim_ens, np.ascontiguousarray(state_p[f.slice]),
            np.asfortranarray(ens_p[f.slice, :]), 1, par.COMM_filter)
        state_p[f.slice] = state_f

    print(' ' * 8 + 'Ensemble standard deviation (estimated RMS error)')
    for f, sd in zip(sv.sfields, ens_stddev):
        print(' ' * 8 + f'{"stddev-" + anastr:>13s}    {f.name:>10s}  {sd:12.4E}')

    # *** Write ensemble and state estimate (not at initial time) ***
    if not _firsttime:
        print(' ' * 8 + '--- write ensemble and state estimate')
        stepstr = f'{abs(step):02d}'
        for f in sv.sfields:
            for member in range(dim_ens):
                _write_field(f'ens{f.name}_{member + 1:02d}_step{stepstr}_{anastr}.txt',
                             ens_p[f.slice, member])
        for f in sv.sfields:
            _write_field(f'state{f.name}_step{stepstr}_{anastr}.txt',
                         state_p[f.slice])

    _firsttime = False

    return state_p, uinv, ens_p
