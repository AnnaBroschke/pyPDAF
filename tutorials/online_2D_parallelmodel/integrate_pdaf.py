"""Time stepping of the parallel model with PDAF (translation of integrate_pdaf.F90)."""
import mod_model as model
import mod_parallel_model as pm
from assimilate_pdaf import assimilate_pdaf
from model_step import model_step


def integrate_pdaf() -> None:
    """Integrate the model and call PDAF after each step."""
    if pm.mype_world == 0:
        print(' START INTEGRATION')
    for step in range(1, model.total_steps + 1):
        if pm.mype_world == 0:
            print(' step', step)
        model_step()
        assimilate_pdaf()
