"""Time stepping of the parallel model with PDAF (translation of online_2D_parallelmodel_fullpar/integrate_pdaf.F90).

Runs only on the model processes."""
import mod_model as model
import mod_parallel_model as pm
import mod_parallel_pdaf as par
from assimilate_pdaf import assimilate_pdaf
from model_step import model_step


def integrate_pdaf() -> None:
    """Integrate the model and call PDAF after each step."""
    first = par.task_id == 1 and pm.mype_2Dmodel == 0
    if first:
        print(' MODEL: START INTEGRATION')
    for step in range(1, model.total_steps + 1):
        if first:
            print(' step', step)
        model_step()
        assimilate_pdaf()
