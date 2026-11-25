"""Initialise model information (translation of initialize.F90).

In the offline mode there is no model. We only need to know the size of the
grid and of the state vector.
"""
import mod_assimilation as assim
import mod_model_pdaf as model
import mod_parallel_pdaf as par


def initialize() -> None:
    """Set grid size and state dimension."""
    model.nx = 36    # Extent of grid in x-direction
    model.ny = 18    # Extent of grid in y-direction

    # State vector dimension: here only one 2D field
    assim.dim_state_p = model.nx * model.ny

    if par.mype_world == 0:
        print(' INITIALIZE MODEL INFORMATION FOR PDAF OFFLINE MODE')
        print(' ' * 22 + 'MODEL: 2D Offline Example for Tutorial')
        print(' ' * 24 + f'Grid size:{model.nx:4d} x {model.ny:4d}')
        print(' ' * 5 + f'Global model state dimension:{assim.dim_state_p:7d}')
