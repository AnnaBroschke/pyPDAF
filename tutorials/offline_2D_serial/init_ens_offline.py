"""Initialise the ensemble (translation of init_ens_offline.F90).

This is a call-back routine that is called by PDAF during PDAF3_init.
The ensemble members are read from files ``../inputs_offline/ens_X.txt``.

Note on array ordering: The Fortran code stores the 2D field (ny, nx)
column by column in the state vector, i.e. the index i (y-direction)
runs fastest: state index = (j-1)*ny + i. In numpy this corresponds to
``field.ravel(order='F')``.
"""
import numpy as np

import mod_model_pdaf as model


def init_ens_offline(filtertype: int, dim_p: int, dim_ens: int,
                     state_p: np.ndarray, uinv: np.ndarray,
                     ens_p: np.ndarray, flag: int):
    """Read the ensemble from files.

    Parameters
    ----------
    filtertype : int
        Type of filter to initialize
    dim_p : int
        PE-local state dimension
    dim_ens : int
        Size of ensemble
    state_p : ndarray (dim_p)
        PE-local model state (not used here)
    uinv : ndarray (dim_ens-1, dim_ens-1)
        Not used for ensemble filters
    ens_p : ndarray (dim_p, dim_ens)
        PE-local state ensemble (filled here)
    flag : int
        PDAF status flag

    Returns
    -------
    state_p, uinv, ens_p, flag
        In Python the modified arrays are returned to PDAF.
    """
    print('\n' + ' ' * 9 + 'Initialize state ensemble')
    print(' ' * 9 + '--- read ensemble from files')
    print(' ' * 9 + f'--- Ensemble size:  {dim_ens:5d}')

    for member in range(dim_ens):
        # Read field of shape (ny, nx); member index is 1-based in the files
        field = np.loadtxt(f'../inputs_offline/ens_{member + 1}.txt')
        assert field.shape == (model.ny, model.nx)

        # Store field column-wise in the state vector (same as Fortran)
        ens_p[:, member] = field.ravel(order='F')

    return state_p, uinv, ens_p, flag
