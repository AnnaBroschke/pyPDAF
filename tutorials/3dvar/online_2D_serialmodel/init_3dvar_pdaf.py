"""Initialise state and B^1/2 for parameterized 3D-Var (translation of init_3dvar_pdaf.F90).

Call-back routine called by PDAF3_init for subtype 0. B^1/2 (Vmat_p) is built
from the ``dim_cvec`` ensemble files::

    state_p = mean of the members
    Vmat_p  = (member - state_p) / sqrt(dim_cvec - 1)

The background state is returned as the single column of ``ens_p``.
"""
import numpy as np

import mod_assimilation as assim


def init_3dvar_pdaf(filtertype: int, dim_p: int, dim_ens: int,
                    state_p: np.ndarray, uinv: np.ndarray,
                    ens_p: np.ndarray, flag: int):
    """Read the ensemble, compute B^1/2 and the background state."""
    print('\n' + ' ' * 9 + 'Initialize state and B^1/2 for 3D-Var')
    print(' ' * 9 + '--- read ensemble from files')
    print(' ' * 9 + f'--- members in B^1/2:  {assim.dim_cvec:5d}')

    invdim_ens = 1.0 / assim.dim_cvec
    prefix = 'ens' if assim.ensgroup == 1 else 'ensB'

    assim.Vmat_p = np.zeros((dim_p, assim.dim_cvec), order='F')
    for member in range(assim.dim_cvec):
        field = np.loadtxt(f'../../inputs_online/{prefix}_{member + 1}.txt')
        assim.Vmat_p[:, member] = field.ravel(order='F')

    print(' ' * 9 + 'Initialize B^1/2')
    state_p[:] = 0.0
    for member in range(assim.dim_cvec):          # same summation order as Fortran
        state_p[:] += assim.Vmat_p[:, member]
    state_p[:] = invdim_ens * state_p

    for member in range(assim.dim_cvec):
        assim.Vmat_p[:, member] -= state_p

    fact = 1.0 / np.sqrt(assim.dim_cvec - 1)
    assim.Vmat_p *= fact

    ens_p[:, 0] = state_p

    return state_p, uinv, ens_p, flag
