"""Initialise the ensemble (translation of online_2D_parallelmodel/init_ens_pdaf.F90).

Each filter process reads the ensemble files and keeps its ``nx_p`` columns.
"""
import numpy as np

import mod_assimilation as assim
import mod_model as model
import mod_parallel_pdaf as par


def init_ens_pdaf(filtertype: int, dim_p: int, dim_ens: int,
                  state_p: np.ndarray, uinv: np.ndarray,
                  ens_p: np.ndarray, flag: int):
    """Read the ensemble and keep the process-local columns."""
    if par.mype_filter == 0:
        print('\n' + ' ' * 9 + 'Initialize state ensemble')
        print(' ' * 9 + '--- read ensemble from files')
        print(' ' * 9 + f'--- Ensemble size:  {dim_ens:5d}')

    prefix = 'ens' if assim.ensgroup == 1 else 'ensB'
    j0 = model.nx_p * par.mype_model
    for member in range(dim_ens):
        field = np.loadtxt(f'../inputs_online/{prefix}_{member + 1}.txt')
        ens_p[:, member] = field[:, j0:j0 + model.nx_p].ravel(order='F')

    return state_p, uinv, ens_p, flag
