"""Initialise model information (translation of initialize.F90).

In the offline mode there is no model. We only need to know the size of the
grid and of the state vector.
"""
import mod_assimilation as assim


def initialize() -> None:
    """Set grid size and state dimension."""
    assim.nx = 36    # Extent of grid in x-direction
    assim.ny = 18    # Extent of grid in y-direction

    # State vector dimension: here only one 2D field
    assim.dim_state_p = assim.nx * assim.ny

    print(' INITIALIZE MODEL INFORMATION FOR PDAF OFFLINE MODE')
    print(' ' * 22 + 'MODEL: 2D Offline Example for Tutorial')
    print(' ' * 24 + f'Grid size:{assim.nx:4d} x {assim.ny:4d}')
    print(' ' * 5 + f'Global model state dimension:{assim.dim_state_p:7d}')
