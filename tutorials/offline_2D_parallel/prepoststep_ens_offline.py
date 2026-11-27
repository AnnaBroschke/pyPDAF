"""Pre- and post-step routine (translation of offline_2D_parallel/prepoststep_ens_offline.F90).

The ensemble spread is computed in parallel (PDAF_diag_stddev with
COMM_filter). For writing the files, the process-local parts of ensemble
and state are sent to process 0, which assembles and writes the global fields.
"""
from mpi4py import MPI
import numpy as np
import pyPDAF.PDAF

import mod_assimilation as assim
import mod_model_pdaf as model
import mod_parallel_pdaf as par

# Equivalent to the Fortran variable "LOGICAL, SAVE :: firsttime"
_firsttime = True


def _write_field(filename: str, vec: np.ndarray) -> None:
    """Write a global state vector as 2D field (ny rows, nx columns)."""
    np.savetxt(filename, vec.reshape((model.ny, model.nx), order='F'))


def prepoststep_ens_offline(step: int, dim_p: int, dim_ens: int,
                            dim_ens_p: int, dim_obs_p: int,
                            state_p: np.ndarray, uinv: np.ndarray,
                            ens_p: np.ndarray, flag: int):
    """Analyse the ensemble and write the global fields on process 0."""
    global _firsttime

    if par.mype_filter == 0:
        if _firsttime:
            print(' ' * 8 + 'Analyze forecasted state ensemble')
        else:
            print(' ' * 8 + 'Analyze and write assimilated state ensemble')

    # *** Ensemble mean and standard deviation (parallel over COMM_filter) ***
    state_p, ens_stddev, pdaf_status = pyPDAF.PDAF.diag_stddev(
        dim_p, dim_ens, state_p, ens_p, 1, par.COMM_filter)

    if par.mype_filter == 0:
        print(' ' * 12 + 'RMS error according to sampled standard deviation: '
              f'{ens_stddev:12.4E}')

    if not _firsttime:
        comm_filter = MPI.Comm.f2py(par.COMM_filter)

        # *** Gather the ensemble on process 0 and write it ***
        if par.mype_filter != 0:
            comm_filter.Send(np.ascontiguousarray(ens_p.T), dest=0, tag=1)
        else:
            ens = np.zeros((assim.dim_state, dim_ens), order='F')
            ens[:dim_p, :] = ens_p
            offset = dim_p
            for domain in range(1, par.npes_filter):
                n = int(model.local_dims[domain])
                ens_p_tmp = np.empty((dim_ens, n))       # member-wise, contiguous
                comm_filter.Recv(ens_p_tmp, source=domain, tag=1)
                ens[offset:offset + n, :] = ens_p_tmp.T
                offset += n

            print(' ' * 8 + '--- write ensemble and state estimate')
            for member in range(dim_ens):
                _write_field(f'ens_{member + 1:02d}_ana.txt', ens[:, member])

        # *** Gather the state estimate on process 0 and write it ***
        if par.mype_filter != 0:
            comm_filter.Send(np.ascontiguousarray(state_p), dest=0, tag=1)
        else:
            state = np.zeros(assim.dim_state)
            state[:dim_p] = state_p
            offset = dim_p
            for domain in range(1, par.npes_filter):
                n = int(model.local_dims[domain])
                comm_filter.Recv(state[offset:offset + n], source=domain, tag=1)
                offset += n
            _write_field('state_ana.txt', state)

    _firsttime = False

    return state_p, uinv, ens_p
