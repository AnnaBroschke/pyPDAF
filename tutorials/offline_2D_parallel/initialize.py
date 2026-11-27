"""Initialise model information (translation of offline_2D_parallel/initialize.F90).

Defines the grid and the domain decomposition: the global state vector
(nx*ny values, stored column-wise) is split into ``npes_model`` contiguous
parts of (almost) equal size. Process ``p`` holds the elements
``offset(p) : offset(p) + local_dims[p]``.
"""
import numpy as np

import mod_assimilation as assim
import mod_model_pdaf as model
import mod_parallel_pdaf as par


def initialize() -> None:
    """Set grid size, global state dimension and domain decomposition."""
    model.nx = 36    # Extent of grid in x-direction
    model.ny = 18    # Extent of grid in y-direction

    # Global state dimension
    assim.dim_state = model.nx * model.ny

    if par.mype_world == 0:
        print(' INITIALIZE MODEL INFORMATION FOR PDAF OFFLINE MODE')
        print(' ' * 22 + 'MODEL: 2D Offline Example')
        print(' ' * 24 + f'Grid size:{model.nx:4d} x {model.ny:4d}')
        print(' ' * 5 + f'Global model state dimension:{assim.dim_state:7d}')

    # *** Domain decomposition ***
    # Equal parts; the first processes get one element more if not divisible
    model.local_dims = np.full(par.npes_model, assim.dim_state // par.npes_model, dtype=int)
    model.local_dims[:assim.dim_state - par.npes_model * model.local_dims[0]] += 1

    if par.mype_world == 0:
        print('\n' + ' ' * 2 + f'-- Domain decomposition over each{par.npes_model:3d} PEs')
        for i in range(par.npes_model):
            print(' ' * 5 + f'task {par.task_id:3d} PE(model) {i:3d} '
                  f'dim_local(state): {model.local_dims[i]:5d}')

    # Process-local state dimension
    assim.dim_state_p = int(model.local_dims[par.mype_model])
