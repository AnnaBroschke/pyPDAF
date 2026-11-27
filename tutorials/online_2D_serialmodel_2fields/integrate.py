"""Time stepping of the model without PDAF (translation of integrate.F90).

Writes the true fields after each step to ``true_stepXX.txt`` and ``trueB_stepXX.txt``.
"""
import numpy as np

import mod_model as model
from model_step import model_step


def integrate() -> None:
    """Integrate the model and write the field at each step."""
    print(' START INTEGRATION')
    for step in range(1, model.total_steps + 1):
        print(' step', step)
        model_step()
        np.savetxt(f'true_step{step:02d}.txt', model.field)
        np.savetxt(f'trueB_step{step:02d}.txt', model.fieldB)
