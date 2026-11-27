"""Initialise the model (translation of initialize.F90).

Reads the initial true field. If ``use_pdaf`` is True, PDAF is initialised
as well (in Fortran this is controlled by the preprocessor flag USE_PDAF).
"""
import numpy as np

import mod_model as model


def initialize(use_pdaf: bool = True) -> None:
    """Initialise grid, time stepping and model field."""
    model.nx = 36           # Extent of grid in x-direction
    model.ny = 18           # Extent of grid in y-direction
    model.total_steps = 18  # Number of time steps to perform

    print(' INITIALIZE 2D TUTORIAL MODEL')
    print(' ' * 10 + f'Grid size:{model.nx:4d} x {model.ny:4d}')
    print(' ' * 10 + f'Time steps{model.total_steps:4d}')

    model.field = np.loadtxt('../../inputs_online/true_initial.txt')
    assert model.field.shape == (model.ny, model.nx)

    if use_pdaf:
        from init_pdaf import init_pdaf
        init_pdaf()
