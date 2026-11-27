"""Time stepping of the parallel model without PDAF (translation of integrate.F90).

After each step the local fields are gathered on process 0 and written to
``true_stepXX.txt``.
"""
import numpy as np

import mod_model as model
import mod_parallel_model as pm
from model_step import model_step


def integrate() -> None:
    """Integrate the model and write the global field at each step."""
    if pm.mype_world == 0:
        print(' START INTEGRATION')
    for step in range(1, model.total_steps + 1):
        if pm.mype_world == 0:
            print(' step', step)
        model_step()

        # Gather the field (MPI_Gather of the column blocks)
        blocks = pm.COMM_2Dmodel.gather(model.field_p, root=0)
        if pm.mype_world == 0:
            np.savetxt(f'true_step{step:02d}.txt', np.hstack(blocks))
