"""Initialise the parallel model (translation of online_2D_parallelmodel_fullpar_1fpe/initialize.F90).

Runs only on the model processes.

The domain is decomposed in x-direction: each of the ``npes_2Dmodel``
processes of a model task holds ``nx_p = nx / npes_2Dmodel`` columns. Only
process counts 1, 2, 3, 4, 6, 9 are allowed.
"""
import numpy as np

import mod_model as model
import mod_parallel_model as pm
import mod_parallel_pdaf as par


def initialize(use_pdaf: bool = True) -> None:
    """Initialise grid, decomposition and the process-local field."""
    model.nx = 36           # Extent of grid in x-direction
    model.ny = 18           # Extent of grid in y-direction
    model.total_steps = 18  # Number of time steps to perform

    # *** Domain decomposition ***
    if pm.npes_2Dmodel in (1, 2, 3, 4, 6, 9):
        model.nx_p = model.nx // pm.npes_2Dmodel
    else:
        print(' ERROR: Invalid number of processes', flush=True)
        pm.abort_parallel()

    # Output by the first process of model task 1 (Fortran: #ifdef USE_PDAF)
    first = (par.task_id == 1 and pm.mype_2Dmodel == 0) if use_pdaf else pm.mype_2Dmodel == 0
    if first:
        print(' MODEL-side: INITIALIZE PARALLELIZED 2D TUTORIAL MODEL')
        print(' ' * 10 + f'Grid size:{model.nx:4d} x {model.ny:4d}')
        print(' ' * 10 + f'Time steps{model.total_steps:4d}')
        print('\n' + ' ' * 2 + f'-- Domain decomposition over{pm.npes_2Dmodel:3d} PEs')
        print(' ' * 2 + f'-- local domain sizes (nx_p x ny): {model.nx_p:3d} x{model.ny:3d}')

    # *** Read the global field and keep the local columns ***
    field = np.loadtxt('../inputs_online/true_initial.txt')
    j0 = model.nx_p * pm.mype_2Dmodel
    model.field_p = field[:, j0:j0 + model.nx_p].copy()
