"""Pre- and post-step routine (translation of online_2D_parallelmodel/prepoststep_pdaf.F90).

The spread is computed in parallel (COMM_filter). Process 0 collects the
column blocks of ensemble and state with Send/Recv and writes the files.
"""
from mpi4py import MPI
import numpy as np
import pyPDAF.PDAF

import mod_assimilation as assim
import mod_model as model
import mod_parallel_pdaf as par

# Equivalent to the Fortran variable "LOGICAL, SAVE :: firsttime"
_firsttime = True


def _write_field(filename: str, vec: np.ndarray) -> None:
    """Write a global state vector as 2D field (ny rows, nx columns)."""
    np.savetxt(filename, vec.reshape((model.ny, model.nx), order='F'))


def prepoststep_pdaf(step: int, dim_p: int, dim_ens: int, dim_ens_p: int,
                     dim_obs_p: int, state_p: np.ndarray, uinv: np.ndarray,
                     ens_p: np.ndarray, flag: int):
    """Analyse the ensemble and write the global fields on process 0."""
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

    state_p, ens_stddev, pdaf_status = pyPDAF.PDAF.diag_stddev(
        dim_p, dim_ens, state_p, ens_p, 1, par.COMM_filter)

    if par.mype_filter == 0:
        print(' ' * 12 + 'RMS error according to sampled variance: '
              f'{ens_stddev:12.4E}')

    if not _firsttime:
        comm_filter = MPI.Comm.f2py(par.COMM_filter)
        stepstr = f'{abs(step):02d}'
        nloc = model.nx_p * model.ny       # size of each process-local part

        # *** Ensemble ***
        if par.mype_filter != 0:
            comm_filter.Send(np.ascontiguousarray(ens_p.T), dest=0, tag=1)
        else:
            ens = np.zeros((assim.dim_state, dim_ens), order='F')
            ens[:dim_p, :] = ens_p
            off_p = dim_p
            for domain in range(1, par.npes_filter):
                ens_p_tmp = np.empty((dim_ens, nloc))
                comm_filter.Recv(ens_p_tmp, source=domain, tag=1)
                ens[off_p:off_p + nloc, :] = ens_p_tmp.T
                off_p += nloc
            print(' ' * 8 + '--- write ensemble and state estimate')
            for member in range(dim_ens):
                _write_field(f'ens_{member + 1:02d}_step{stepstr}_{anastr}.txt',
                             ens[:, member])

        # *** State estimate ***
        if par.mype_filter != 0:
            comm_filter.Send(np.ascontiguousarray(state_p), dest=0, tag=1)
        else:
            state = np.zeros(assim.dim_state)
            state[:dim_p] = state_p
            off_p = dim_p
            for domain in range(1, par.npes_filter):
                comm_filter.Recv(state[off_p:off_p + nloc], source=domain, tag=1)
                off_p += nloc
            _write_field(f'state_step{stepstr}_{anastr}.txt', state)

    _firsttime = False

    return state_p, uinv, ens_p
