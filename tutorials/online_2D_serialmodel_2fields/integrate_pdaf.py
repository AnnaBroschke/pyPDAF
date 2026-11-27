"""Time stepping of the model with PDAF (translation of integrate_pdaf.F90).

Compared to integrate.py, only one line is added: after each time step
``assimilate_pdaf()`` is called. PDAF decides whether an analysis is done
at this step (every ``delt_obs`` steps).
"""
import mod_model as model
import mod_parallel_pdaf as par
from assimilate_pdaf import assimilate_pdaf
from model_step import model_step


def integrate_pdaf() -> None:
    """Integrate the model and call PDAF after each step."""
    print(' START INTEGRATION')
    for step in range(1, model.total_steps + 1):
        if par.mype_world == 0:
            print(' step', step)
        model_step()
        assimilate_pdaf()
