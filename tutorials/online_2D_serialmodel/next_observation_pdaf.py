"""Time of next observation (translation of next_observation_pdaf.F90).

Call-back routine that tells PDAF how many time steps the model has to be
integrated until the next analysis step, and whether to exit.
"""
import mod_assimilation as assim
import mod_model as model
import mod_parallel_pdaf as par


def next_observation_pdaf(stepnow: int, nsteps: int, doexit: int, time: float):
    """Return (nsteps, doexit, time).

    As in Fortran, the incoming value of ``nsteps`` is used in the check.
    """
    time = 0.0   # Not used in this implementation

    if stepnow + nsteps <= model.total_steps:
        # *** During the assimilation process ***
        nsteps = assim.delt_obs   # Time steps until next assimilation
        doexit = 0                # Do not exit assimilation
        if par.mype_world == 0:
            print(f'{stepnow:7d}   Next observation at time step{stepnow + nsteps:7d}')
    else:
        # *** End of assimilation process ***
        nsteps = 0                # No more steps
        doexit = 1                # Exit assimilation
        if par.mype_world == 0:
            print(f'{stepnow:7d}   No more observations - end assimilation')

    return nsteps, doexit, time
