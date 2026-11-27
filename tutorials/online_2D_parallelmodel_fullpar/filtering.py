"""Time stepping on the filter processes (translation of filtering.F90).

The filter processes do not run the model. They set up the grid and the
domain decomposition for the filter (nx_p = nx / npes_filter), initialise
PDAF and call assimilate_pdaf in each time step. PDAF receives the forecast
ensemble from the model tasks, computes the analysis and sends it back.
"""
import mod_model as model
import mod_parallel_model as pm
import mod_parallel_pdaf as par
from assimilate_pdaf import assimilate_pdaf
from init_pdaf import init_pdaf


def filtering() -> None:
    """Filter-side initialisation and time loop."""
    model.nx = 36
    model.ny = 18
    model.total_steps = 18

    if par.mype_filter == 0:
        print(' PDAF-side: INITIALIZE PARALLELIZED 2D TUTORIAL MODEL')
        print(' ' * 10 + f'Grid size:{model.nx:4d} x {model.ny:4d}')
        print(' ' * 10 + f'Time steps{model.total_steps:4d}')

    if par.npes_filter in (1, 2, 3, 4, 6, 9):
        model.nx_p = model.nx // par.npes_filter
    else:
        print(' ERROR: Invalid number of processes', flush=True)
        pm.abort_parallel()

    if par.mype_filter == 0:
        print('\n' + ' ' * 2 + f'-- Domain decomposition over{par.npes_filter:3d} PEs')
        print(' ' * 2 + f'-- local domain sizes (nx_p x ny): {model.nx_p:3d} x{model.ny:3d}')

    init_pdaf()

    if par.mype_filter == 0:
        print(' PDAF-side: START INTEGRATION')
    for step in range(1, model.total_steps + 1):
        assimilate_pdaf()
